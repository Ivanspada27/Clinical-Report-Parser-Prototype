# Clinical-Report-Parser-Prototype

# Clinical Report Parser – Prototype

This is a simple prototype I built to automatically extract vital signs from scanned medical reports (like PDFs or images you get after a doctor visit).

It uses OCR (optical character recognition) to read the text, and then applies pattern matching to find values like:

- **Blood pressure**
- **Heart rate**
- **Glucose**
- **Oxygen saturation**
- **Body temperature**
- **Weight and height**
- **BMI** (calculated from weight and height)

The extracted data is cleaned, validated, and saved in a structured **JSON format**, which can then be used for analysis, storage, or further automation.

---

## Why I Built It

I wanted to create something that works on **real clinical documents** — not clean datasets — but scanned reports full of messy formatting, typos, and mixed units.  
This was an experiment to see if I could turn them into usable data automatically.

I built it using **LLMs** (ChatGPT and Claude) to generate and refine the code based on my prompts.  
I focused on defining the problem, designing the structure, running tests, debugging issues, and improving the results.

---

## How It Works

1. You give it a **scanned medical report** (PDF or image)  
2. It runs **OCR** with Tesseract to read the text  
3. It applies **regular expressions** to detect relevant values  
4. It checks if the values are in **realistic medical ranges**  
5. It saves everything in a **clean JSON format**

---

## Note

I didn’t write every line of this by hand. I used LLM to help generate the code, based on my idea and directions.  
But I learned a lot by testing, debugging, and understanding how everything fits together — and now I’m using this as a base to keep growing.
