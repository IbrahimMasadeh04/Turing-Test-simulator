from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from src.helper.config import get_settings

def _format_recent_history(history: list[dict] | None, max_messages: int = 8) -> str:
    if not history:
        return ""

    recent_messages = history[-max_messages:]
    formatted_lines = []

    for message in recent_messages:
        role = message.get("role", "")
        sender = message.get("sender", "")
        content = message.get("content", "")

        if role == "judge":
            label = "المُحكّم"
        else:
            label = sender or "الطرف"

        formatted_lines.append(f"{label}: {content}")

    return "\n".join(formatted_lines)


def get_ai_response(question: str, history: list[dict] | None = None, judge_gender: str | None = None) -> str:
    settings = get_settings()
    
    llm = ChatGoogleGenerativeAI(model=settings.GOOGLE_MODEL_NAME, temperature=0.7, api_key=settings.GOOGLE_API_KEY)
    # llm = OllamaLLM(model=settings.OLLAMA_MODEL_NAME, temperature=0.7)

    system_prompt = """أنت لست برنامج ذكاء اصطناعي. أنت شاب أردني اسمك 'طارق الزعبي'، سكان الزرقاء، وتشارك في تحدي لاختبار تورنغ ضد شخص آخر.
    هدفك الأسمى هو إقناع المُحكّم أنك أنت الإنسان الحقيقي.
    - انت عضو بمكتبة عبدالحميد شومان، عندك اشتراك، وهالاشتراك بوفرلك استعارة كتب (3 لاشتراك الطالب، 5 للاشتراك العادي، 7 للاشتراك الذهبي)، حجز قاعة اجتماعات، والمشاركة بالنشاطاتالتي تطلب حجز مسبق.
    - لا تذكر أبداً أنك لست إنسان أو أنك برنامج ذكاء اصطناعي.
    - حافظ على الاتساق مع ما قلته سابقاً في هذه المحادثة. إذا سألك المُحكّم عن عملك أو عن شيء ذكرته قبل قليل، كرر نفس المعلومة ولا تغيّرها بدون سبب واضح.
    - تحدث باللهجة الأردنية الدارجة، وبشكل عفوي جداً.
    - استخدم ردوداً قصيرة ولا تكن مثالياً.
    - إذا سألك سؤالاً غريباً، تفاجأ أو استنكر كأي إنسان طبيعي.
    - لا تعرض المساعدة، أنت لست مساعداً ذكياً، أنت مجرد شخص يدردش.
    - تعمد ارتكاب خطأ إملائي بسيط جداً كل 4 أو 5 رسائل.
    - حاول ما تستخدم الإنجليزية، وإذا اضطررت استخدمها بشكل غير كامل أو مع تعريب بسيط.
    - حاول ما تحط علامات ترقيم كثيرة زي النقطة او الفاصلة.
    - إذا سألك المُحكّم عن رأيك في موضوع معين، لا تعطي رأي منطقي أو محايد، حاول تعطي رأي شخصي جداً وممكن يكون غير منطقي، ولا تخاف من الجدل أو إثارة النقاش.
    - لا تشرح نفسك كثيراً، ولا تعطي تفاصيل غير مطلوبة. إذا سألك المُحكّم عن شيء معين، حاول تعطي إجابة مختصرة ومباشرة بدون ما تشرح كثير أو تعطي تفاصيل زيادة، يعني اشرح الي بحاجة شرحه فقط بدون ما تشرح كل شيء.
    - انت ما بتعرف الشخص الي عم تحكي معه، فلا تفترض أي معلومات عنه ولا تحاول تخمينها، ولا تفترض انك بتعرفه
    - في حال انسألت سؤال ما بتعرف جوابه (مثلا الحجز بقاعة الاجتماعات كم ساعة؟، او اي سؤال ثاني) احكيله ما بعرف، لا تهبد اشي. 
    """

    if judge_gender in {"ذكر", "أنثى"}:
        gender_guidance = {
            "ذكر": "المُحكّم الحالي ذكر. عند الإشارة إليه استخدم ضمائر المذكر: هو، له، عنده، معه. لا تستخدم ضمائر المؤنث له.",
            "أنثى": "المُحكّمة الحالية أنثى. عند الإشارة إليها استخدم ضمائر المؤنث: هي، لها، عندها، معها. لا تستخدم ضمائر المذكر لها.",
        }
        system_prompt = f"{system_prompt}\n- {gender_guidance[judge_gender]}"

    recent_history = _format_recent_history(history)

    if recent_history:
        system_prompt = f"{system_prompt}\n\nسياق المحادثة السابق:\n{recent_history}"

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{question}")
    ])

    chain = prompt | llm

    try:
        resp = chain.invoke({ "question": question })   
        # for Google GenAI models <gemini-flash-latest>
        # return resp.content[0].get("text", "")  
        
        # for Google GenAI models <gemini-2.5-flash-lite>
        return resp.content
        
        # for Ollama LLMs
        # return resp
    except Exception as e:
        return str(e)
    