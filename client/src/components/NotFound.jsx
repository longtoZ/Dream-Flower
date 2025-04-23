import React from 'react';

const wordArrays = [
    [
      'Computer Vision',
      'Neural Networks',
      'Image Recognition',
      'Convolution',
      'Object Detection',
      'Feature Extraction',
      'Segmentation',
      'Optical Flow',
      'Pose Estimation',
      'Depth Estimation',
    ],
    [
      'Data Science',
      'Machine Learning',
      'Regression',
      'Clustering',
      'Data Mining',
      'Time Series',
      'Classification',
      'Anomaly Detection',
      'Data Wrangling',
      'Visualization',
    ],
    [
      'Audio Processing',
      'Signal Processing',
      'Spectrogram',
      'Speech Recognition',
      'Audio Synthesis',
      'Noise Reduction',
      'Echo Cancellation',
      'Frequency Analysis',
      'Voice Activity',
      'Sound Localization',
    ],
    [
      'Deep Learning',
      'GANs',
      'Reinforcement Learning',
      'Transfer Learning',
      'Autoencoders',
      'Recurrent Networks',
      'Attention Models',
      'Gradient Descent',
      'Backpropagation',
      'Overfitting',
    ],
    [
      'Natural Language',
      'Sentiment Analysis',
      'Tokenization',
      'Word Embeddings',
      'Text Generation',
      'Named Entity',
      'Topic Modeling',
      'Machine Translation',
      'Chatbots',
      'Text Summarization',
    ],
    [
      'Big Data',
      'Feature Engineering',
      'Dimensionality Reduction',
      'Hyperparameter Tuning',
      'Cross Validation',
      'Ensemble Methods',
      'Bayesian Inference',
      'Graph Analytics',
      'Stream Processing',
      'Model Evaluation',
    ],
];

const NotFound = () => {
    return (
        <div className="relative flex flex-col items-center justify-center h-full overflow-hidden cursor-default" style={{ height: '100vh'}}>
        {/* Background Typography */}
        <div className="absolute inset-0 z-0 opacity-30">
            <div className="flex flex-col h-full">
            {wordArrays.map((wordArray, rowIndex) => (
            <div
              key={rowIndex}
              className="flex flex-nowrap animate-marquee flex-1"
            >
              {wordArray.map((word, index) => (
                <span
                  key={index}
                  className="text-zinc-500 font-mono text-8xl font-bold opacity-50 mx-6 whitespace-nowrap hover:text-white hover:opacity-100 transition duration-500 ease-in-out"
                >
                  {word}
                </span>
              ))}
              {/* Duplicate for seamless looping */}
              {wordArray.map((word, index) => (
                <span
                  key={`duplicate-${index}`}
                  className="text-zinc-500 font-mono text-8xl font-bold opacity-50 mx-6 whitespace-nowrap hover:text-white hover:opacity-100 transition duration-500 ease-in-out"
                >
                  {word}
                </span>
              ))}
            </div>
          ))}
                </div>
        </div>

        {/* Main Content */}
        <div className="relative z-10 flex flex-col items-center justify-center h-full">
            <h1 className="text-[10rem] font-bold text-white">404</h1>
            <h2 className="text-4xl font-bold text-white">No data received</h2>
            <button
            className="mt-4 px-6 py-3 bg-transparent text-white rounded-md border border-zinc-500 cursor-pointer hover:bg-zinc-300 hover:text-black transition duration-200"
            onClick={() => (window.location.href = '/extract')}
            >
            Back to home
            </button>
        </div>

        <style>
            {`
            @keyframes marquee {
                0% {
                transform: translateX(0);
                }
                100% {
                transform: translateX(-50%);
                }
            }
            .animate-marquee {
                animation: marquee 40s linear infinite;
                display: flex;
            }
            .animate-marquee:nth-child(odd) {
                animation-direction: reverse;
            }
            .typography-cloud:hover {
                animation-play-state: paused; /* Optional: Pause on hover */
            }
            `}
        </style>
        </div>
    );
};

export default NotFound;