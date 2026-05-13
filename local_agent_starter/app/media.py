from __future__ import annotations

import base64
from pathlib import Path
from typing import Any

from openai import OpenAI

from .config import Settings


def _media_client(settings: Settings) -> OpenAI:
    if not settings.has_multimodal_api:
        raise RuntimeError(
            "A chave LOCAL_AGENT_MULTIMODAL_API_KEY nao esta configurada. "
            "Defina essa variavel ou OPENAI_API_KEY para usar audio e imagem."
        )
    return OpenAI(
        base_url=settings.multimodal_base_url,
        api_key=settings.multimodal_api_key,
    )


def generate_image(
    settings: Settings,
    prompt: str,
    output_path: Path,
    size: str,
    quality: str,
) -> dict[str, Any]:
    client = _media_client(settings)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    response = client.images.generate(
        model=settings.image_model,
        prompt=prompt,
        size=size,
        quality=quality,
        output_format="png",
    )
    image_base64 = response.data[0].b64_json
    output_path.write_bytes(base64.b64decode(image_base64))
    return {
        "ok": True,
        "path": str(output_path),
        "model": settings.image_model,
        "size": size,
        "quality": quality,
    }


def transcribe_audio_file(settings: Settings, audio_path: Path) -> dict[str, Any]:
    client = _media_client(settings)
    with audio_path.open("rb") as audio_file:
        response = client.audio.transcriptions.create(
            model=settings.transcription_model,
            file=audio_file,
            response_format="text",
        )

    text = response if isinstance(response, str) else getattr(response, "text", str(response))
    return {
        "ok": True,
        "path": str(audio_path),
        "model": settings.transcription_model,
        "text": text.strip(),
    }


def record_microphone(output_path: Path, seconds: int, sample_rate: int = 16000) -> dict[str, Any]:
    try:
        import sounddevice as sd
        import soundfile as sf
    except ImportError as exc:  # pragma: no cover - depends on local environment
        raise RuntimeError(
            "As dependencias de captura de audio nao estao instaladas. "
            "Instale sounddevice e soundfile."
        ) from exc

    output_path.parent.mkdir(parents=True, exist_ok=True)
    frames = int(seconds * sample_rate)
    recording = sd.rec(frames, samplerate=sample_rate, channels=1, dtype="float32")
    sd.wait()
    sf.write(output_path, recording, sample_rate)
    return {
        "ok": True,
        "path": str(output_path),
        "seconds": seconds,
        "sample_rate": sample_rate,
    }


def speak_text(text: str, rate: int, voice_hint: str = "") -> dict[str, Any]:
    try:
        import pyttsx3
    except ImportError as exc:  # pragma: no cover - depends on local environment
        raise RuntimeError("A dependencia pyttsx3 nao esta instalada.") from exc

    engine = pyttsx3.init()
    engine.setProperty("rate", rate)

    if voice_hint:
        for voice in engine.getProperty("voices"):
            voice_text = f"{voice.id} {voice.name}".lower()
            if voice_hint.lower() in voice_text:
                engine.setProperty("voice", voice.id)
                break

    engine.say(text)
    engine.runAndWait()
    return {"ok": True, "spoken_characters": len(text)}
