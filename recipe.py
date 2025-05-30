from flask import Flask, render_template, request
import os
from dotenv import load_dotenv
import google.generativeai as genai


# Flask 앱 초기화
app = Flask(__name__)

cuisines = [
    "",
    "Italian",
    "Mexican",
    "Chinese",
    "Indian",
    "Japanese",
    "Thai",
    "French",
    "Mediterranean",
    "American",
    "Greek",
]

# create a dictionary to store the languages and their corresponding codes
languages = {
    'English': 'en',
    'Spanish': 'es',
    'French': 'fr',
    'German': 'de',
    'Russian': 'ru',
    'Chinese (Simplified)': 'zh-CN',
    'Chinese (Traditional)': 'zh-TW',
    'Japanese': 'ja',
    'Korean': 'ko',
    'Italian': 'it',
    'Portuguese': 'pt',
    'Arabic': 'ar',
    'Dutch': 'nl',
    'Swedish': 'sv',
    'Turkish': 'tr',
    'Greek': 'el',
    'Hebrew': 'he',
    'Hindi': 'hi',
    'Indonesian': 'id',
    'Thai': 'th',
    'Filipino': 'tl',
    'Vietnamese': 'vi'
    # ... potentially more based on actual Whisper support
}


dietary_restrictions = [
    "Gluten-Free",
    "Dairy-Free",
    "Vegan",
    "Pescatarian",
    "Nut-Free",
    "Kosher",
    "Halal",
    "Low-Carb",
    "Organic",
    "Locally Sourced"
]


load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')

# Google Gemini API 설정
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

@app.route('/')
def index():
    return render_template('index.html',
                           cuisines=cuisines,
                           dietary_restrictions=dietary_restrictions,
                           languages=languages)

@app.route('/generate_recipe', methods=['POST'])
def generate_recipe():
    # 사용자 입력 받기
    ingredients = request.form.getlist('ingredient')
    selected_cuisine = request.form.get('cuisine')
    selected_restrictions = request.form.getlist('restrictions')
    selected_language = request.form.get('language')

    print('selected_cuisine: ' + selected_cuisine)
    print('selected_restrictions: ' + str(selected_restrictions))
    print('selected_language: ' + selected_language)

    if len(ingredients) != 3:
        return "Kindly provide exactly 3 ingredients."

    # ✅ 언어 이름 추출 (언어 코드 → 사람 이름)
    language_name = next(
        (lang for lang, code in languages.items() if code == selected_language),
        selected_language
    )

    # ✅ 프롬프트 구성
    prompt = f"""Write the following recipe in {language_name}.
It should be styled as an HTML page.
The recipe is based on these ingredients: {', '.join(ingredients)}.
You may add supporting ingredients if necessary.
List the ingredients at the top, then the step-by-step instructions."""

    if selected_cuisine:
        prompt += f" The cuisine should be {selected_cuisine}."

    if selected_restrictions:
        prompt += f" Please follow these dietary restrictions: {', '.join(selected_restrictions)}."

    # Gemini API 호출
    try:
        response = model.generate_content(prompt)
        recipe = response.text
    except Exception as e:
        recipe = f"Error generating recipe: {str(e)}"

    return render_template('recipe.html', recipe=recipe)

if __name__ == '__main__':
    app.run(debug=True)
