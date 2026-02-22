import React, { useState } from 'react';
import { fakerCN } from './logic/faker';
import { generateLifeStory, generateAvatar } from './api/ai';
import PersonaCard from './components/PersonaCard';
import ApiSettings from './components/ApiSettings';
import ScrambleText from './components/ScrambleText';

function App() {
  const [persona, setPersona] = useState(null);
  const [avatarUrl, setAvatarUrl] = useState('');
  const [lifeStory, setLifeStory] = useState('');
  const [isLoadingAI, setIsLoadingAI] = useState(false);
  const [showSettings, setShowSettings] = useState(false);

  // User's provided keys from global context 
  const [dsKey, setDsKey] = useState('');
  const [sfKey, setSfKey] = useState('');

  const handleGenerate = async () => {
    // 1. Generate base data instantly
    const newPersona = fakerCN.generatePersona();
    setPersona(newPersona);

    // Clear previous AI state
    setAvatarUrl('');
    setLifeStory('');
    setIsLoadingAI(true);

    // 2. Fetch AI assets in parallel if keys are present
    const t0 = performance.now();
    try {
      const [story, avatar] = await Promise.all([
        generateLifeStory(newPersona, dsKey),
        generateAvatar(newPersona, sfKey)
      ]);
      setLifeStory(story);
      setAvatarUrl(avatar);
    } catch (e) {
      console.error(e);
      setLifeStory("获取故事失败，网络错误或被限流。");
      setAvatarUrl("https://api.dicebear.com/9.x/avataaars-neutral/svg?seed=" + newPersona.ssn);
    } finally {
      // Ensure the "decryption" visual lasts at least 1.5s for the cyber vibe
      const renderDelay = Math.max(0, 1500 - (performance.now() - t0));
      setTimeout(() => setIsLoadingAI(false), renderDelay);
    }
  };

  return (
    <div style={{ position: 'relative' }}>
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '3rem' }}>
        <div>
          <h1 className="text-gradient" style={{ margin: 0, fontSize: '2.5rem', letterSpacing: '2px' }}>
            <ScrambleText text="CYBER CREATOR" duration={2000} />
          </h1>
          <p style={{ color: 'var(--text-secondary)', margin: '0.5rem 0 0', letterSpacing: '1px', textTransform: 'uppercase' }}>
            Faker-CN: High-Fidelity Persona Engine
          </p>
        </div>

        <button className="cyber-button secondary" onClick={() => setShowSettings(true)} style={{ padding: '0.5rem 1rem', fontSize: '0.8rem' }}>
          <span>设置 / SETTINGS</span>
        </button>
      </header>

      {showSettings && (
        <ApiSettings
          dsKey={dsKey} setDsKey={setDsKey}
          sfKey={sfKey} setSfKey={setSfKey}
          onClose={() => setShowSettings(false)}
        />
      )}

      <main style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>

        {!persona ? (
          <div style={{ textAlign: 'center', marginTop: '10vh' }}>
            <div style={{ fontSize: '3rem', color: 'rgba(255,255,255,0.05)', marginBottom: '2rem' }}>
              [ SYSTEM INITIALIZED ]
            </div>
            <p style={{ color: 'var(--text-secondary)', maxWidth: '600px', margin: '0 auto 3rem', lineHeight: '1.8' }}>
              欢迎连接中国大陆高保真虚拟数据生成引擎。点击下方按钮，开始随机推演一位逻辑绝对自洽的超写式虚拟人物。
            </p>
            <button className="cyber-button animate-pulse-glow" onClick={handleGenerate} style={{ padding: '1.2rem 3rem', fontSize: '1.4rem' }}>
              创造数字生命 / INITIALIZE
            </button>
          </div>
        ) : (
          <>
            <div style={{ width: '100%', display: 'flex', justifyContent: 'flex-end', marginBottom: '-1rem', zIndex: 10 }}>
              <button className="cyber-button" onClick={handleGenerate} disabled={isLoadingAI}>
                {isLoadingAI ? '推演中...' : '重新生成 / REGENERATE'}
              </button>
            </div>
            <PersonaCard
              persona={persona}
              avatarUrl={avatarUrl}
              lifeStory={lifeStory}
              isLoadingAI={isLoadingAI}
            />
          </>
        )}

      </main>

    </div>
  );
}

export default App;
