import React, { useState } from 'react';

const ApiSettings = ({ dsKey, setDsKey, sfKey, setSfKey, onClose }) => {
    return (
        <div style={{
            position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
            backgroundColor: 'rgba(0,0,0,0.8)',
            backdropFilter: 'blur(5px)',
            display: 'flex', justifyContent: 'center', alignItems: 'center',
            zIndex: 9999
        }}>
            <div className="glass-panel" style={{ width: '400px', maxWidth: '90%' }}>
                <h3 style={{ marginTop: 0, color: 'var(--primary-glow)' }}>[ SYSTEM . CONFIG ]</h3>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '1.5rem' }}>
                    为开启高阶“赛博造物主”能力（生成超写实照片及深刻生平），请输入以下 API 密钥。数据仅在浏览器本地调用，不经过任何中间服务器。
                </p>

                <div style={{ marginBottom: '1rem' }}>
                    <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--primary-glow)', marginBottom: '0.5rem' }}>DeepSeek API Key (生成故事)</label>
                    <input
                        type="password"
                        value={dsKey}
                        onChange={e => setDsKey(e.target.value)}
                        placeholder="sk-..."
                        style={{ width: '100%', padding: '0.8rem', boxSizing: 'border-box', background: 'rgba(0,0,0,0.5)', border: '1px solid var(--glass-border)', color: 'white', borderRadius: '4px', outline: 'none' }}
                    />
                </div>

                <div style={{ marginBottom: '1.5rem' }}>
                    <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--secondary-glow)', marginBottom: '0.5rem' }}>SiliconFlow API Key (生成证件照)</label>
                    <input
                        type="password"
                        value={sfKey}
                        onChange={e => setSfKey(e.target.value)}
                        placeholder="sk-..."
                        style={{ width: '100%', padding: '0.8rem', boxSizing: 'border-box', background: 'rgba(0,0,0,0.5)', border: '1px solid var(--glass-border)', color: 'white', borderRadius: '4px', outline: 'none' }}
                    />
                </div>

                <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '1rem' }}>
                    <button className="cyber-button" onClick={onClose} style={{ padding: '0.6rem 1.2rem', fontSize: '0.9rem' }}>
                        保存 / SAVE
                    </button>
                </div>
            </div>
        </div>
    );
};

export default ApiSettings;
