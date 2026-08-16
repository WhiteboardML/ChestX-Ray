import os
import torch
import logging
from PIL import Image
from typing import Dict, List, Optional
from transformers import Qwen2_5_VLForConditionalGeneration, AutoProcessor
from peft import PeftModel
from qwen_vl_utils import process_vision_info

logger = logging.getLogger("chest_xray_backend")

# Global singletons to prevent multiple loads of 7B weights
_vlm_model = None
_vlm_processor = None

# Absolute path to LoRA weights
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
LORA_PATH = os.path.join(PROJECT_ROOT, "outputs_qwen2_5_vl_7b_cxr_lora_model")

def get_vlm_model_and_processor():
    """
    Load Qwen2.5-VL base model and local QLoRA fine-tuned adapter.
    """
    global _vlm_model, _vlm_processor
    if _vlm_model is not None and _vlm_processor is not None:
        return _vlm_model, _vlm_processor

    logger.info("Initializing Qwen2.5-VL-7B-Instruct with fine-tuned CXR QLoRA weights...")
    if not os.path.exists(LORA_PATH):
        raise FileNotFoundError(f"QLoRA weights not found at: {LORA_PATH}")

    # Set appropriate device map and precision
    if torch.cuda.is_available():
        device = "cuda"
        torch_dtype = torch.bfloat16
        device_map = "auto"
    elif torch.backends.mps.is_available():
        device = "mps"
        torch_dtype = torch.float16
        device_map = "auto"
    else:
        device = "cpu"
        torch_dtype = torch.float32
        device_map = "cpu"

    try:
        logger.info(f"Loading processor/tokenizer from {LORA_PATH}...")
        _vlm_processor = AutoProcessor.from_pretrained(LORA_PATH)

        base_model_name = "Qwen/Qwen2.5-VL-7B-Instruct"
        logger.info(f"Loading base model {base_model_name}...")
        
        # Load base model. On Mac, we handle quantization fallback or MPS parameters
        if device == "mps":
            # bitsandbytes 4-bit is CUDA-only, so we load in float16 for MPS
            base_model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
                base_model_name,
                torch_dtype=torch_dtype,
                device_map=device_map
            )
        elif device == "cuda":
            # CUDA supports 4-bit quantization natively via bitsandbytes
            base_model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
                base_model_name,
                torch_dtype=torch_dtype,
                device_map=device_map,
                load_in_4bit=True
            )
        else:
            base_model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
                base_model_name,
                torch_dtype=torch_dtype,
                device_map=device_map
            )

        logger.info(f"Loading Peft adapter model from {LORA_PATH}...")
        _vlm_model = PeftModel.from_pretrained(base_model, LORA_PATH)
        logger.info("Qwen2.5-VL with LoRA weights loaded successfully.")
        return _vlm_model, _vlm_processor
    except Exception as e:
        logger.error(f"Error loading Qwen2.5-VL model/adapter: {e}", exc_info=True)
        raise e

def run_vlm_audit(
    image_path: str,
    symptoms: List[str],
    temperature: Optional[float] = None,
    spo2: Optional[int] = None,
    crp_level: Optional[float] = None,
    wbc_count: Optional[float] = None,
    vit_diagnosis: Optional[str] = None,
    vit_score: Optional[float] = None
) -> Dict[str, any]:
    """
    Run multimodal Qwen2.5-VL analysis on X-ray + clinical context.
    """
    try:
        model, processor = get_vlm_model_and_processor()
    except Exception as e:
        logger.error(f"Could not initialize Qwen2.5-VL: {e}")
        # Fallback if weights cannot be loaded locally
        return {
            "diagnosis": vit_diagnosis or "Tahlil qilinmadi",
            "rationale": f"VLM modelini yuklashda xatolik: {str(e)}",
            "conflicting_signals": "Aniqlanmadi",
            "suggested_actions": "Shifokor nazorati"
        }
    
    # Construct clinical details block
    symptoms_str = ", ".join(symptoms) if symptoms else "Yo'q"
    temp_str = f"{temperature} °C" if temperature else "Aniqlanmagan"
    spo2_str = f"{spo2}%" if spo2 else "Aniqlanmagan"
    crp_str = f"{crp_level} mg/L" if crp_level else "Aniqlanmagan"
    wbc_str = f"{wbc_count} x10^9/L" if wbc_count else "Aniqlanmagan"
    vit_info = f"AI Vision Prediction: {vit_diagnosis} ({vit_score}% probability)" if vit_diagnosis else "N/A"

    prompt = f"""Tibbiy tahlil va rentgenogramma audit hisoboti:
[Bemor Simptomlari]: {symptoms_str}
[Tana harorati]: {temp_str}
[Oksigenatsiya (SpO2)]: {spo2_str}
[CRP (C-Reaktiv Protein)]: {crp_str}
[WBC (Leykotsitlar)]: {wbc_str}
[Dastlabki AI Vision Tahlili]: {vit_info}

Rentgenogrammani va bemor klinik parametrlarini tahlil qiling. 
Quyidagi formatda javob bering:
1. Diagnosis: [Uzbek tilidagi yakuniy diagnostik xulosa]
2. Diagnostic Rationale: [Nima sababdan bu tashxis qo'yilganligi haqida batafsil tushuntirish]
3. Conflicting Signals: [Agar rentgen va laboratoriya ma'lumotlari o'rtasida farq bo'lsa, ularni ko'rsating]
4. Suggested Actions: [Keyingi tavsiya etiladigan amallar yoki tekshiruvlar]
"""

    messages = [
        {
            "role": "user",
            "content": [
                {"type": "image", "image": image_path},
                {"type": "text", "text": prompt}
            ]
        }
    ]

    try:
        text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        image_inputs, video_inputs = process_vision_info(messages)
        inputs = processor(
            text=[text],
            images=image_inputs,
            videos=video_inputs,
            padding=True,
            return_tensors="pt"
        )
        
        # Move inputs to same device as model
        device = next(model.parameters()).device
        inputs = {k: v.to(device) if torch.is_tensor(v) else v for k, v in inputs.items()}

        # Generate response
        with torch.no_grad():
            generated_ids = model.generate(**inputs, max_new_tokens=512)
            generated_ids_trimmed = [
                out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs["input_ids"], generated_ids)
            ]
            output_text = processor.batch_decode(
                generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
            )[0]
        
        parsed_result = parse_vlm_output(output_text)
        return parsed_result
    except Exception as e:
        logger.error(f"VLM audit execution failed: {e}", exc_info=True)
        return {
            "diagnosis": vit_diagnosis or "Tahlil qilib bo'lmadi",
            "rationale": f"VLM tahlilida xatolik yuz berdi: {str(e)}",
            "conflicting_signals": "Aniqlanmadi",
            "suggested_actions": "Vrach ko'rigini tashkil etish"
        }

def parse_vlm_output(text: str) -> Dict[str, str]:
    """Helper to parse Qwen2.5-VL text output into structured keys."""
    result = {
        "diagnosis": "",
        "rationale": "",
        "conflicting_signals": "Yo'q",
        "suggested_actions": ""
    }
    
    current_key = None
    lines = text.strip().split("\n")
    for line in lines:
        line_lower = line.lower()
        if "1. diagnosis:" in line_lower:
            current_key = "diagnosis"
            result["diagnosis"] = line.split(":", 1)[1].strip()
        elif "2. diagnostic rationale:" in line_lower:
            current_key = "rationale"
            result["rationale"] = line.split(":", 1)[1].strip()
        elif "3. conflicting signals:" in line_lower:
            current_key = "conflicting_signals"
            result["conflicting_signals"] = line.split(":", 1)[1].strip()
        elif "4. suggested actions:" in line_lower:
            current_key = "suggested_actions"
            result["suggested_actions"] = line.split(":", 1)[1].strip()
        elif current_key:
            result[current_key] += " " + line.strip()

    # Cleanup
    for k in result:
        result[k] = result[k].strip()
        
    return result
