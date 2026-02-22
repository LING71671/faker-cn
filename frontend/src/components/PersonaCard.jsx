import React from 'react';
import ScrambleText from './ScrambleText';

const PersonaCard = ({ persona, avatarUrl, lifeStory, isLoadingAI }) => {
    if (!persona) return null;

    return (
        <div className="glass-panel animate-fade-in" style={{ width: '100%', maxWidth: '800px', margin: '2rem auto' }}>

            <div style={{ display: 'flex', gap: '2rem', flexWrap: 'wrap' }}>

                {/* Left Column: Avatar & Core Info */}
                <div style={{ flex: '1 1 200px', display: 'flex', flexDirection: 'column', gap: '1rem', alignItems: 'center' }}>
                    <div
                        style={{
                            width: '180px', height: '240px',
                            borderRadius: '8px',
                            overflow: 'hidden',
                            border: '2px solid var(--primary-glow)',
                            boxShadow: '0 0 15px rgba(0, 229, 255, 0.3)',
                            backgroundColor: 'rgba(0,0,0,0.5)',
                            display: 'flex', justifyContent: 'center', alignItems: 'center'
                        }}
                    >
                        {isLoadingAI ? (
                            <div style={{ color: 'var(--primary-glow)', textAlign: 'center' }}>
                                <p className="animate-pulse-glow" style={{ boxShadow: 'none', margin: 0, fontSize: '24px' }}>⠇</p>
                                <small>生成写实中...</small>
                            </div>
                        ) : (
                            <img src={avatarUrl} alt="Avatar" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                        )}
                    </div>

                    <h2 style={{ margin: 0, color: 'var(--primary-glow)', fontSize: '2rem', letterSpacing: '4px' }}>
                        <ScrambleText text={persona.name} />
                    </h2>
                    <div style={{ background: 'var(--glass-bg)', padding: '0.2rem 1rem', borderRadius: '4px', border: '1px solid rgba(255,255,255,0.1)' }}>
                        <ScrambleText text={`${persona.gender} / ${persona.age}岁`} />
                    </div>
                </div>

                {/* Right Column: Detailed Specs */}
                <div style={{ flex: '2 1 300px', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>

                    <div>
                        <h4 style={{ color: 'var(--text-secondary)', marginBottom: '0.5rem', textTransform: 'uppercase', fontSize: '0.8rem', letterSpacing: '2px' }}>身份证条码 / SSN</h4>
                        <div style={{ fontFamily: 'monospace', fontSize: '1.4rem', color: 'var(--text-primary)', letterSpacing: '2px' }}>
                            <ScrambleText text={persona.ssn} duration={1200} />
                        </div>
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
                        <InfoItem label="出生日期" text={persona.birth_date} />
                        <InfoItem label="户籍地" text={`${persona.hometown.province} ${persona.hometown.city} ${persona.hometown.area}`} />
                        <InfoItem label="职业档案" text={persona.social.job} />
                        <InfoItem label="预估月薪" text={persona.social.salary} delay={1500} />
                        <InfoItem label="名下车辆" text={persona.asset.vehicle_plate} />
                        <InfoItem label="预估存款" text={persona.asset.deposit} delay={1500} />
                        <InfoItem label="主用邮箱 (Email)" text={persona.email} />
                    </div>

                    <div style={{ marginTop: 'auto', paddingTop: '1rem', borderTop: '1px solid var(--glass-border)' }}>
                        <a href={`https://yopmail.com/?${persona.yopmail_login}`} target="_blank" rel="noreferrer"
                            style={{ color: 'var(--secondary-glow)', textDecoration: 'none', display: 'inline-flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.9rem' }}>
                            <span className="cyber-button secondary" style={{ padding: '0.5rem 1rem', fontSize: '0.8rem' }}>
                                进入 Yopmail 收件箱 &rarr;
                            </span>
                        </a>
                    </div>

                </div>

            </div>

            {/* AI Life Story Section */}
            <div style={{ marginTop: '2rem', paddingTop: '1.5rem', borderTop: '1px dashed rgba(0, 229, 255, 0.3)' }}>
                <h4 style={{ color: 'var(--text-secondary)', marginBottom: '1rem', textTransform: 'uppercase', fontSize: '0.8rem', letterSpacing: '2px' }}>
                    <span style={{ color: 'var(--primary-glow)', marginRight: '8px' }}>[ AI 分析 ]</span>
                    人生轨迹脉络扫描 (Life Story Pattern)
                </h4>

                <div style={{
                    lineHeight: 1.8,
                    color: 'var(--text-primary)',
                    fontSize: '1rem',
                    background: 'rgba(0,0,0,0.3)',
                    padding: '1.5rem',
                    borderRadius: '8px',
                    borderLeft: '4px solid var(--primary-glow)'
                }}>
                    {isLoadingAI ? (
                        <div style={{ color: 'var(--primary-glow)' }}>
                            <p className="animate-pulse-glow" style={{ boxShadow: 'none', margin: 0, display: 'inline-block', marginRight: '10px' }}>⠇</p>
                            <ScrambleText text="正在调用 DeepSeek 大模型推演人物数字档案..." duration={20000} />
                        </div>
                    ) : (
                        lifeStory ? <p style={{ margin: 0 }}>{lifeStory}</p> : <ScrambleText text="未检测到 AI 配置，跳过轨迹生成。" />
                    )}
                </div>
            </div>

        </div>
    );
};

const InfoItem = ({ label, text, delay = 800 }) => (
    <div>
        <div style={{ color: 'var(--text-secondary)', fontSize: '0.75rem', marginBottom: '0.2rem', textTransform: 'uppercase', letterSpacing: '1px' }}>{label}</div>
        <div style={{ color: 'var(--text-primary)', fontWeight: '500' }}>
            <ScrambleText text={text} duration={delay} />
        </div>
    </div>
);

export default PersonaCard;
