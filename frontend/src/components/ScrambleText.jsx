import React, { useState, useEffect } from 'react';

const ScrambleText = ({ text, className, duration = 800 }) => {
    const [displayText, setDisplayText] = useState('');

    useEffect(() => {
        if (!text) return;

        const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*';
        let iteration = 0;
        let interval = null;

        // How many times to scramble per letter
        const MAX_ITERATIONS = Math.max(10, Math.floor(duration / 30));

        clearInterval(interval);

        interval = setInterval(() => {
            setDisplayText(prev => {
                return text
                    .split('')
                    .map((letter, index) => {
                        if (index < iteration) {
                            return text[index];
                        }
                        return chars[Math.floor(Math.random() * chars.length)];
                    })
                    .join('');
            });

            if (iteration >= text.length) {
                clearInterval(interval);
            }

            iteration += 1 / 2; // Speed of resolving characters
        }, 30);

        return () => clearInterval(interval);
    }, [text, duration]);

    return <span className={className}>{displayText}</span>;
};

export default ScrambleText;
