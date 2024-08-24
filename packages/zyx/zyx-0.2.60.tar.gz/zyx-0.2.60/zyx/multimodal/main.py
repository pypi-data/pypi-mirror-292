from typing import Literal, Optional, Any, Union

__all__ = ["image", "audio"]

ModelType = Literal[
    "dall-e-2", "dall-e-3",
    "flux-dev", "flux-realism", "flux-schnell", "flux-pro", "flux-lora", "flux-general",
    "aura", "sd-v3", "fooocus"
]

PREDEFINED_APPS: Literal[
    "fal-ai/flux/dev",
    "fal-ai/flux-realism",
    "fal-ai/flux/schnell",
    "fal-ai/flux-pro",
    "fal-ai/flux-lora",
    "fal-ai/flux-general",
    "fal-ai/aura-flow",
    "fal-al/lora",
    "fal-ai/stable-diffusion-v3-medium",
    "fal-ai/fooocus",
] = None

def _get_model_config(model: ModelType):
    dall_e_models = ["dall-e-2", "dall-e-3"]
    fal_models = {
        "flux-dev": "fal-ai/flux/dev",
        "flux-realism": "fal-ai/flux-realism",
        "flux-schnell": "fal-ai/flux/schnell",
        "flux-pro": "fal-ai/flux-pro",
        "flux-lora": "fal-ai/flux-lora",
        "flux-general": "fal-ai/flux-general",
        "aura": "fal-ai/aura-flow",
        "sd-v3": "fal-ai/stable-diffusion-v3-medium",
        "fooocus": "fal-ai/fooocus"
    }
    
    if model in dall_e_models:
        return {"provider": "openai", "model": model}
    elif model in fal_models:
        return {"provider": "fal", "application": fal_models[model]}
    else:
        raise ValueError(f"Unsupported model: {model}")

def image(
    prompt: str,
    model: ModelType = "dall-e-3",
    api_key: Optional[str] = None,
    image_size: Optional[str] = "landscape_4_3",
    num_inference_steps: Optional[int] = 26,
    guidance_scale: Optional[float] = 3.5,
    enable_safety_checker: Optional[bool] = False,
    size: Optional[str] = "1024x1024",
    quality: Optional[str] = "standard",
    n: Optional[int] = 1,
) -> Union[str, Any]:
    model_config = _get_model_config(model)
    
    if model_config["provider"] == "openai":
        from openai import OpenAI
        try:
            client = OpenAI(api_key=api_key)
        except Exception as e:
            return e
        try:
            response = client.images.generate(
                model=model_config["model"],
                prompt=prompt,
                size=size,
                quality=quality,
                n=n,
            )
        except Exception as e:
            return e
        return response.data[0].url
    elif model_config["provider"] == "fal":
        import fal_client
        try:
            handler = fal_client.submit(
                application=model_config["application"],
                arguments={
                    "prompt": prompt,
                    "image_size": image_size,
                    "num_inference_steps": num_inference_steps,
                    "guidance_scale": guidance_scale,
                    "enable_safety_checker": enable_safety_checker,
                    "num_images": n,
                }
            )
            result = handler.get()
        except Exception as e:
            result = e
        return result
    
OPENAI_TTS_MODELS = Literal["tts-1", "tts-1-hd"]  
OPENAI_TTS_VOICES = Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
 
def openai_text_to_speech(
    prompt : str = None,
    model : Optional[OPENAI_TTS_MODELS] = "tts-1",
    voice : Optional[OPENAI_TTS_VOICES] = "alloy",
    api_key : Optional[str] = None,
    base_url : Optional[str] = None,
):
    from openai import OpenAI
    
    client = OpenAI(api_key = api_key,
                    base_url = base_url)
    
    try:
        speech = client.audio.speech.create(
            input = prompt,
            model = model,
            voice = voice
        )
    except Exception as e:
        return e
    
    return speech    

def openai_speech_to_text(
    model : Optional[str] = "whisper-1",
    api_key : Optional[str] = None,
    base_url : Optional[str] = None,
    organization : Optional[str] = None,
    file : Optional[str] = None
):
    from openai import OpenAI
    
    client = OpenAI(api_key = api_key, base_url = base_url,
                    organization = organization)
    
    if file:
        if not file.endswith(".mp3"):
            raise ValueError("File must be a .mp3 file")
        audio_file = open(file, "rb")
        
    try:
        transcription = client.audio.transcriptions.create(
            model = model,
            file = audio_file,  
            response_format = "text" 
        )
        return transcription
    except Exception as e:
        return e 

if __name__ == "__main__":
    print(image(model = "flux-dev", prompt = "A beautiful landscape painting of a sunset over the ocean.", n = 1))