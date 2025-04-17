const express = require('express');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const pdfParse = require('pdf-parse');
const textract = require('textract');
const util = require('util');
const FormData = require('form-data');
const cors = require('cors');
const WordExtractor = require("word-extractor"); 

const app = express();
const upload = multer({ dest: 'uploads/' });

app.use(express.urlencoded({ extended: true }));
app.use(express.json());

app.use(express.static("dist"));

const clearUploadsFolder = () => {
  const directory = path.join(__dirname, 'uploads');

  fs.readdir(directory, (err, files) => {
    if (err) return console.error('Failed to list directory:', err);

    for (const file of files) {
      fs.unlink(path.join(directory, file), err => {
        if (err) console.error(`Failed to delete ${file}:`, err);
      });
    }
  });
};

app.post('/upload', upload.single('file'), async (req, res) => {
    const file = req.file;
    const purpose = req.body.purpose;
    console.log(file);
    console.log(purpose);
    if (!file) return res.status(400).json({ error: 'No file uploaded' });
  
    try {
      const ext = path.extname(file.originalname).toLowerCase();
      let extractedText = '';
  
      if (ext === '.pdf') {
        extractedText = await extractFromPDF(file.path);
      } else if (ext === '.txt') {
        extractedText = fs.readFileSync(file.path, 'utf-8');
      } else if (ext === '.docx' || ext === '.doc') {
        const extractor = new WordExtractor();
        const extracted = await extractor.extract(file.path);
        extractedText = extracted._body;
      } else if(ext === '.wav') {
        const response = await fetch("http://127.0.0.1:3000/audio-transcribe", {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
          },
        });
        const data = await response.json();
        extractedText = data.transcription;
      } else {
        return res.status(400).json({ error: 'Unsupported file type' });
      }
  
      const cleanedText = preprocessText(extractedText);
      const summary = await generateSummary(cleanedText, purpose);

      console.log("Summary:", summary);
  
      clearUploadsFolder();
  
      res.status(200).json({ summary });
  
    } catch (err) {
      console.error(err);
      res.status(500).json({ error: 'Internal server error' });
    }
});

const preprocessText = (text) => {
    return text
      .replace(/\s+/g, ' ')
      .replace(/[^a-zA-Z0-9 .,?!]/g, '')
      .trim();
};

const generateSummary = async (text, purpose) => {
// Replace this with your actual model call or local pipeline
    const response = await fetch("http://127.0.0.1:3000/summarize", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            text: text,
            purpose: purpose
        }),
    });

    const data = await response.json();
    return data;
};

const extractFromPDF = async (filePath) => {
    const dataBuffer = fs.readFileSync(filePath);
    const data = await pdfParse(dataBuffer);
    return data.text;
};

app.post('/youtube', async (req, res) => {
  try {
    console.log("Received request to /youtube endpoint");
    const videoUrl = req.body.url;

    const regex = /(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:watch\?v=|embed\/|v\/|shorts\/)|youtu\.be\/)([a-zA-Z0-9_-]{11})/;
    const match = videoUrl.match(regex);
    const videoId = match ? match[1] : null;

    const response = await fetch('http://localhost:3000/get-transcript', {
      method: 'POST',
      body: JSON.stringify({
        videoId: videoId,
        purpose: req.body.purpose || 'default',
      }),
      headers: {
        'Content-Type': 'application/json',
      },
    })

    const summary = await response.json();
    res.status(200).json({ summary });
  } catch(error) {
    console.error(error);
    return res.status(500).json({ error });
  }
});

const { YtDlp } = require('ytdlp-nodejs');
const { get } = require('http');
const ytdlp = new YtDlp();

const downloadYTAudio = async (url) => {
  ytdlp.downloadAsync(url, {
    extractAudio: true,
    audioFormat: 'wav',
    output: 'downloaded_audio.%(ext)s',
  }).then(output => {
    console.log('Download completed:', output);
  }).catch(error => {
    console.error('Error:', error);
  });
};

downloadYTAudio('https://www.youtube.com/watch?v=4WEQtgnBu0I')

app.listen(8000, () => {
    console.log('Server is running on port 8000');
});