# report_generator.py
import google.generativeai as genai
import json
import os

# Gemini API key 
os.environ["GEMINI_API_KEY"] = "REPLACE_WITH_REAL_API_KEY"
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

def generate_analysis(detected_type, features):
    """
    Generate personalised analysis text using Google Gemini API.
    Sends extracted handwriting features to Gemini and returns
    dynamic, contextual analysis text for the screening report.
    """

    solidity     = features.get("solidity", 0)
    ink_ratio    = features.get("ink_ratio", 0)
    num_contours = features.get("num_contours", 0)
    extent       = features.get("extent", 0)
    ink_pixels   = features.get("ink_pixels", 0)
    aspect_ratio = features.get("aspect_ratio", 0)

    prompt = f"""
You are a medical AI assistant specialized in analyzing handwriting patterns for Parkinson's Disease screening.

A patient has completed a {detected_type} handwriting test. Below are the extracted image features from their drawing:

- Pattern Type: {detected_type}
- Solidity Score: {solidity:.4f} (measures stroke smoothness; lower = more irregular)
- Ink Ratio: {ink_ratio:.4f} (measures drawing coverage; lower = sparse/incomplete)
- Number of Contours: {int(num_contours)} (measures stroke fragmentation; higher = more breaks)
- Extent: {extent:.4f} (measures how well drawing fills bounding box)
- Ink Pixels: {int(ink_pixels)} (total drawn pixels)
- Aspect Ratio: {aspect_ratio:.4f} (shape proportion of drawing)

Based on these features, generate a clinical-style analysis with exactly these three sections.
Reason across ALL features together, not individually.
Be specific, reference the actual values, and write in a professional but accessible tone.

You MUST respond in this exact JSON format only, with absolutely no extra text, no markdown, no backticks:
{{
    "stroke_regularity": "2-3 sentence analysis of stroke regularity based on solidity and contour data",
    "drawing_coverage": "2-3 sentence analysis of drawing coverage based on ink ratio and pixel data",
    "pattern_complexity": "2-3 sentence analysis of pattern complexity based on contour count and extent"
}}
"""

    try:
        model    = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)
        raw_text = response.text.strip()

        # Clean if wrapped in markdown backticks
        if "```" in raw_text:
            raw_text = raw_text.split("```")[1]
            if raw_text.startswith("json"):
                raw_text = raw_text[4:]
            raw_text = raw_text.strip()

        # Clean any leading/trailing non-JSON text
        start = raw_text.find("{")
        end   = raw_text.rfind("}") + 1
        if start != -1 and end != 0:
            raw_text = raw_text[start:end]

        result = json.loads(raw_text)

        return {
            "stroke_regularity":  result.get("stroke_regularity",  _fallback_regularity(detected_type, solidity)),
            "drawing_coverage":   result.get("drawing_coverage",   _fallback_coverage(detected_type, ink_ratio)),
            "pattern_complexity": result.get("pattern_complexity", _fallback_complexity(detected_type, num_contours)),
        }

    except Exception as e:
        print(f"GEMINI ERROR: {e}")  
        return {
            "stroke_regularity":  _fallback_regularity(detected_type, solidity),
            "drawing_coverage":   _fallback_coverage(detected_type, ink_ratio),
            "pattern_complexity": _fallback_complexity(detected_type, num_contours),
        }

# Fallback rule-based (used if API fails) 

def _fallback_regularity(detected_type, solidity):
    is_spiral = detected_type == "Spiral"
    if is_spiral:
        if solidity < 0.45:
            return (f"Significant irregularity detected in stroke patterns "
                    f"(solidity score: {solidity:.2f}). The spiral strokes show "
                    f"notable deviations from a smooth continuous curve, which may "
                    f"indicate motor control difficulties.")
        elif solidity < 0.70:
            return (f"Mild irregularity detected in stroke patterns "
                    f"(solidity score: {solidity:.2f}). The spiral strokes show "
                    f"some minor deviations from a smooth curve, which may warrant "
                    f"further observation.")
        else:
            return (f"Stroke patterns appear consistent and well-formed "
                    f"(solidity score: {solidity:.2f}). The spiral strokes follow "
                    f"a relatively smooth continuous curve with no significant "
                    f"irregularities detected.")
    else:
        if solidity < 0.40:
            return (f"Significant irregularity detected in stroke patterns "
                    f"(solidity score: {solidity:.2f}). The meander strokes show "
                    f"notable deviations from even zigzag lines, which may indicate "
                    f"motor control difficulties.")
        elif solidity < 0.65:
            return (f"Mild irregularity detected in stroke patterns "
                    f"(solidity score: {solidity:.2f}). The meander strokes show "
                    f"some unevenness in the zigzag pattern, which may warrant "
                    f"further observation.")
        else:
            return (f"Stroke patterns appear consistent and well-formed "
                    f"(solidity score: {solidity:.2f}). The meander strokes follow "
                    f"a relatively even zigzag pattern with no significant "
                    f"irregularities detected.")

def _fallback_coverage(detected_type, ink_ratio):
    is_spiral = detected_type == "Spiral"
    if is_spiral:
        if ink_ratio < 0.08:
            return (f"Very low ink coverage detected (ink ratio: {ink_ratio:.3f}). "
                    f"The spiral drawing appears sparse or incomplete, which may "
                    f"suggest reduced drawing pressure or difficulty completing "
                    f"the full pattern.")
        elif ink_ratio < 0.25:
            return (f"Moderate ink coverage detected (ink ratio: {ink_ratio:.3f}). "
                    f"The spiral drawing shows reasonable coverage across the canvas "
                    f"with some areas of lower density.")
        else:
            return (f"Good ink coverage detected (ink ratio: {ink_ratio:.3f}). "
                    f"The spiral drawing shows consistent ink distribution "
                    f"across the canvas, suggesting steady drawing pressure "
                    f"throughout the pattern.")
    else:
        if ink_ratio < 0.10:
            return (f"Very low ink coverage detected (ink ratio: {ink_ratio:.3f}). "
                    f"The meander drawing appears sparse or incomplete, which may "
                    f"suggest reduced drawing pressure or difficulty completing "
                    f"the full pattern.")
        elif ink_ratio < 0.30:
            return (f"Moderate ink coverage detected (ink ratio: {ink_ratio:.3f}). "
                    f"The meander drawing shows reasonable coverage across the canvas "
                    f"with some variation in line density.")
        else:
            return (f"Good ink coverage detected (ink ratio: {ink_ratio:.3f}). "
                    f"The meander drawing shows consistent ink distribution "
                    f"across the canvas, suggesting steady drawing pressure "
                    f"throughout the pattern.")

def _fallback_complexity(detected_type, num_contours):
    is_spiral = detected_type == "Spiral"
    if is_spiral:
        if num_contours > 25:
            return (f"Highly fragmented stroke pattern detected "
                    f"(contour count: {int(num_contours)}). The spiral shows a large "
                    f"number of disconnected stroke segments, which may indicate "
                    f"tremor-related interruptions in the drawing motion.")
        elif num_contours > 8:
            return (f"Some stroke fragmentation noted "
                    f"(contour count: {int(num_contours)}). The spiral contains "
                    f"a moderate number of stroke segments, suggesting minor "
                    f"interruptions in the drawing motion.")
        else:
            return (f"Stroke continuity appears normal "
                    f"(contour count: {int(num_contours)}). The spiral is composed "
                    f"of few stroke segments, indicating a smooth and continuous "
                    f"drawing motion with minimal interruptions.")
    else:
        if num_contours > 35:
            return (f"Highly fragmented stroke pattern detected "
                    f"(contour count: {int(num_contours)}). The meander shows a large "
                    f"number of disconnected stroke segments, which may indicate "
                    f"tremor-related interruptions in the drawing motion.")
        elif num_contours > 12:
            return (f"Some stroke fragmentation noted "
                    f"(contour count: {int(num_contours)}). The meander contains "
                    f"a moderate number of stroke segments, suggesting minor "
                    f"interruptions in the drawing motion.")
        else:
            return (f"Stroke continuity appears normal "
                    f"(contour count: {int(num_contours)}). The meander is composed "
                    f"of few stroke segments, indicating a smooth and continuous "
                    f"drawing motion with minimal interruptions.")