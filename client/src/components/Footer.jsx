import React from 'react'

import GitHubIcon from '@mui/icons-material/GitHub';
import InstagramIcon from '@mui/icons-material/Instagram';
import EmailIcon from '@mui/icons-material/Email';

const Footer = () => {
  return (
    <footer className="w-full mt-40 bg-[#30323b75] backdrop-blur-md border-t border-gray-700 px-10 py-10 text-sm text-gray-400">
      <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-4 gap-8 mt-10">
        
        {/* Quote */}
        <div className="text-left text-2xl font-semibold text-gray-300">
          “Where petals whisper secrets, where dreams find their wings.”
        </div>

        {/* Navigation */}
        <div className="flex flex-col gap-3 text-gray-300">
          <span className="font-semibold text-white text-lg">Links</span>
          <a href="/about" className="hover:text-white transition">About</a>
          <a href="/contact" className="hover:text-white transition">Contact</a>
          <a href="/privacy" className="hover:text-white transition">Privacy</a>
        </div>

        {/* Socials */}
        <div className="flex flex-col gap-2 text-gray-300">
          <span className="font-semibold text-white text-lg">Follow Me</span>
          <div className="flex gap-3">
            <a href="https://github.com" className="hover:text-white">
              <GitHubIcon className="text-3xl" style={{fontSize:'1.6rem'}}/>
            </a>
            <a href="https://instagram.com" className="hover:text-white">
              <InstagramIcon className="text-3xl" style={{fontSize:'1.6rem'}}/>
            </a>
            <a href="mailto:hello@flowerdance.com" className="hover:text-white">
              <EmailIcon className="text-3xl" style={{fontSize:'1.6rem'}}/>
            </a>
          </div>
        </div>

        {/* Newsletter */}
        <div className="flex flex-col gap-3">
          <span className="font-semibold text-white text-lg">Subscribe to my newsletter</span>
          <form className="flex gap-2">
            <input
              type="email"
              placeholder="you@example.com"
              className="bg-primary text-white px-3 py-2 rounded-lg text-sm focus:outline-none w-full"
            />
            <button
              type="submit"
              className="bg-zinc-100 text-gray-800 px-4 py-2 rounded-lg transition duration-100 ease cursor-pointer"
            >
              <span className="align-middle text-base">Send</span>
            </button>
          </form>
        </div>
      </div>

      {/* Bottom note */}
      <div className="mt-20 text-center text-xs text-gray-500">
        &copy; 2025 Dream Flower. All rights reserved.
      </div>
    </footer>
  )
}

export default Footer