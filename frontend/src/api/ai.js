// Browser-side AI fetch logic

export async function generateLifeStory(persona, apiKey) {
    if (!apiKey) return "暂无AI故事（API密钥未配置）";

    const prompt = `你是一个深谙中国社会百态的现实主义作家。请根据以下人物属性，用100字左右为他/她写一段极其真实、带有时代感和生活气息的个人微型传记。不要写套话，要像真实的社会档案。\n\n人物信息：\n${JSON.stringify(persona, null, 2)}`;

    try {
        const res = await fetch("https://api.deepseek.com/chat/completions", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${apiKey}`
            },
            body: JSON.stringify({
                model: "deepseek-chat",
                messages: [{ role: "user", content: prompt }],
                temperature: 0.7,
                max_tokens: 200
            })
        });

        const data = await res.json();
        if (data.choices && data.choices.length > 0) {
            return data.choices[0].message.content.trim();
        }
        return "生成失败，请检查配置。";
    } catch (e) {
        console.error("Story generation failed", e);
        return "请求出错，请检查网络或密钥有效性。";
    }
}

export async function generateAvatar(persona, apiKey) {
    if (!apiKey) return "https://api.dicebear.com/9.x/avataaars-neutral/svg?seed=" + persona.ssn;

    const prompt = `A highly realistic, photographic, frontal extreme close-up portrait of a Chinese ${persona.gender === '男' ? 'man' : 'woman'}, age ${persona.age}, job is ${persona.social.job}. Standard 3:4 ID photo format with a solid blue background (#438EDB). Highly detailed skin texture, natural lighting, looking straight at the camera. Authentic everyday look.`;

    try {
        const res = await fetch("https://api.siliconflow.cn/v1/images/generations", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${apiKey}`
            },
            body: JSON.stringify({
                model: "black-forest-labs/FLUX.1-schnell",
                prompt: prompt,
                image_size: "768x1024",
                num_inference_steps: 4, // FLUX.1-schnell works great with fewer steps
                batch_size: 1,
                seed: Math.floor(Math.random() * 9999999999)
            })
        });

        const data = await res.json();
        if (data.images && data.images.length > 0) {
            return data.images[0].url;
        }
    } catch (e) {
        console.error("Avatar generation failed", e);
    }
    return "https://api.dicebear.com/9.x/avataaars-neutral/svg?seed=" + persona.ssn;
}
