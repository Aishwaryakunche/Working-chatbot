import string
import random
from flask import Flask, request, jsonify
from flask_cors import CORS
from spellchecker import SpellChecker
from fuzzywuzzy import fuzz
import nltk
from nltk.stem import WordNetLemmatizer

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Download required NLTK resources
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('omw-1.4')

lemmatizer = WordNetLemmatizer()

def LemTokens(tokens):
    return [lemmatizer.lemmatize(token) for token in tokens]

remove_punct_dict = dict((ord(punct), None) for punct in string.punctuation)

def LemNormalize(text):
    return LemTokens(nltk.word_tokenize(text.lower().translate(remove_punct_dict)))

spell = SpellChecker()

def correct_spelling(text):
    corrected_text = []
    words = text.split()
    for word in words:
        correction = spell.correction(word)
        corrected_text.append(correction if correction else word)
    return " ".join(corrected_text)

class Rulebot:
    greeting_responses = (
        "Welcome to HireStar.io! I'm Star Guide, your virtual assistant for all things hiring. What can I do for you today?",
        "Hello and welcome to HireStar.io! I'm Star Guide, here to help you with your hiring needs. How can I assist you?",
        "Hi there! This is Star Guide from HireStar.io. How can I help you today?",
        "Hello! I'm Star Guide, your personal assistant at HireStar.io. How can I be of service to you today?",
        "Welcome to HireStar.io! I'm Star Guide, here to assist you. What would you like to know?",
        "Hi! You've reached HireStar.io. I'm Star Guide, your virtual guide. How can I assist you with your hiring queries?",
        "Hello and welcome! This is Star Guide from HireStar.io. How can I help make your hiring process easier today?",
        "Hi there! I'm Star Guide, your assistant at HireStar.io. What hiring-related questions can I help answer for you?",
        "Welcome! I'm Star Guide, the virtual assistant for HireStar.io. How can I assist you with your hiring needs today?"
    )
    exiting_inputs = (
        "bye", "goodbye, thanks", "see you later", "i need to go now", "exit chat", "close chat window",
        "no more questions for now.", "end conversation.", "stop chatting.", "that's all for now.",
        "close chat window.", "exit chat", "end conversation"
    )
    exiting_responses = (
        "Thank you for chatting with me! If you have any more questions, feel free to return. Have a great day!",
        "It was a pleasure assisting you. If you need further help, don't hesitate to reach out. Goodbye!",
        "Thank you for visiting HireStar.io. If you have more questions in the future, I'm here to help. Take care!",
        "I'm glad I could help. If you have any more queries, come back anytime. Have a wonderful day!",
        "Thank you for your time. Should you have more questions, feel free to ask. Goodbye!",
        "It was nice assisting you today. If you need any more information, don't hesitate to chat again. Goodbye!",
        "Thank you for using HireStar.io's services. Have a great day, and feel free to return if you need more help!",
        "I hope I was able to assist you. If you need anything else, I'm here. Have a great day ahead!",
        "Thanks for chatting with HireStar.io. If you have more questions, I'm always here to help. Farewell!",
        "Thank you for your time and inquiries. Should you need further assistance, please return. Goodbye and take care!"
    )


intent_keywords = {
    'greetings': ["hi", "hey", "hello", "greetings", "good morning", "good afternoon", "good evening"],
    'exiting_inputs': ["bye", "goodbye, thanks", "see you later"],
    'CEO':['ceo?','who is the ceo of hirestar.io','who is the leader of hirestar.io'],
    'company_name': ['company name', 'your company', 'what is your company called', 'what is your company name'],
    'who are you':['who are you', 'what is your name', 'introduce yourself', 'tell me about yourself', 'who is this','your name please'],
    'services': ['services', 'services you offer', 'provide','can you do','services provided','available services','services you provide','what services do you offer'],
    'blockchain': ['use blockchain', 'leveraging blockchain', 'utilize blockchain technology', 'blockchain for verification'],
    'why hirestar.io': ['why hirestar.io', 'why choose', 'why hirestar', 'why should I hire'],
    'what is hirestar.io': ['what is hirestar.io', 'what is your website', 'what does hirestar.io','website name', 'your website', 'what is your website called', 'what is your website name','this website'],
    'language': ['language', 'languages','multi-language','languagesupport','languagebarrier','worldwideusers','preferredlanguage'],
    'what is blockchain technology': ['what is blockchain technology','explain blockchain technology','define blockchain technology','blockchain technology explanation','blockchain technology definition','how does blockchain technology work','blockchain technology overview','understanding blockchain technology','describe blockchain technology'],
    'how do you manage risk': ['manage risk', 'reduce risk', 'risk management','how do you manage risk','risk management','how is risk managed','managing risk','reducing risk','risk mitigation','risk control','risk assessment','risk prevention','risk reduction'],
    'why did you choose blockchain technology': ['why blockchain among all', 'blockchain better', 'why blockchain','why did you choose blockchain technique','why blockchain','why blockchain technology','why use blockchain','advantages of blockchain','benefits of blockchain','reasons for blockchain','choosing blockchain','blockchain advantages'],
    'Hirestar API': ['Hirestar API', 'API', 'api integration'],
    'products': ['products', 'product offerings', 'what products'],
    'identity verification': ['identity verification', 'verify identity', 'ID verification', 'confirm identity','verify identity documents', 'authenticate identity', 'ID check', 'identity confirmation','identity validation', 'proof of identity'],
    'degree verification': ['degree verification', 'verify educational qualifications', 'academic credentials verification','verify academic credentials', 'educational qualifications verification', 'validate degrees','academic background check', 'degree authentication', 'confirm educational qualifications'],
    'employment verification': ['employment verification','past employement', 'verify work history', 'job verification','verify employment history', 'work experience verification', 'job history check','employment background check', 'confirm work details', 'validate job history'],
    'financial integrity checks': ['financial integrity checks', 'financial audit', 'financial transparency verification','financial credibility verification', 'audit financial records', 'financial background check','financial history verification', 'financial transparency validation', 'check financial integrity'],
    'crime check verification': ['crime check verification', 'criminal background check', 'legal history verification','crime check', 'criminal record check', 'background investigation', 'criminal background verification', 'legal background check','criminal history validation', 'confirm legal history'],
    'Experience and Employee Background Verification powered by Blockchain': ['experience', 'employee background verification', 'verification powered by blockchain'],
    'blockchain technology enhance the verification process': ['blockchain technology enhance', 'how blockchain enhance', 'blockchain verification process'],
    'blockchain verification more secure than traditional methods': ['blockchain verification more secure', 'why blockchain secure', 'blockchain vs traditional'],
    'types of employee information can be verified using this service': ['types of employee information', 'what can be verified', 'employee information verification'],
    'time taken for verification process': ['time taken for verification process', 'how long does verification take', 'verification time frame', 'time for background check', 'duration of verification', 'processing time for verification', 'how much time'],
    'accessibility of information stored on the block chain': ['accessibility of information', 'who can access', 'information access blockchain'],
    'transparency and trust': ['transparency and trust', 'trust verification', 'transparent verification'],
    'thanks': ['thanks', 'thank you', 'appreciate it', 'thanks a lot', 'thank you very much', 'thanks so much', 'thanks a bunch'],
    'goodbye': ['bye', 'goodbye', 'see you', 'talk to you later', 'catch you later', 'bye bye'],
    'affirmation': ['yes', 'yeah', 'yep', 'sure', 'absolutely', 'definitely', 'of course'],
    'negation': ['no', 'nope', 'not really', 'not at all'],
    'confusion': ['I don\'t understand', 'confused', 'can you explain', 'don\'t get it', 'what do you mean', 'clarify'],
    'small talk': ['how are you', 'how\'s it going', 'what\'s up', 'how are things', 'how do you do'],
    'dissatisfaction': ['not correct', 'incorrect', 'wrong', 'not helpful', 'doesn\'t help', 'bad answer'],
    'completion': ['nothing else', 'that\'s all', 'no more questions', 'I\'m done', 'thank you, nothing else'],
    'anything else':['okay','ok',"fine","alright","that's nice"],
    'contact':['contact','get in touch','contact information','contact info','how to reach you'],
    'pricing':['pricing','cost','price','how much','fee'],
    'support':['support','help','assistance','need help','customer support'],
    'privacy':['privacy policy','data protection','how is my data used','data privacy']
}


def classify_intent(text):
    corrected_text = correct_spelling(text)
    max_similarity = 0
    best_intent = 'default'
    for intent, keywords in intent_keywords.items():
        for keyword in keywords:
            similarity = fuzz.partial_ratio(corrected_text, keyword)
            if similarity > max_similarity:
                max_similarity = similarity
                best_intent = intent
    return best_intent

def generate_response(intent):
    responses = {
        'greetings': random.choice(Rulebot.greeting_responses),
        'exiting': random.choice(Rulebot.exiting_responses),
        'CEO':"The CEO of Hirestar.io is B.Praful Vinayak",
        'company_name': "I work for HireStar.io, a company specializing in blockchain-powered background verification services. How can I assist you further?",
        'anything else': "Is there anything else you would like to know? I'm here to help with any questions or information you need.",
        'contact':"You can contact us through our website's contact form, email us at support@hirestar.io, or call us at +1-800-HIRE-STAR. We are here to assist you with any inquiries.",
        'pricing':"Our pricing varies depending on the specific services you require. Please visit our pricing page on HireStar.io or contact our sales team for a detailed quote.",
        'support': "Our support team is available 24/7 to assist you. You can reach out to us via the support portal on our website, or email us at support@hirestar.io.",
        'privacy':"At HireStar.io, we take your privacy seriously. You can read our full privacy policy on our website to understand how we protect and use your data.",
        'who are you': "I'm Star Guide, your virtual assistant at HireStar.io. I'm an AI designed to assist you with all your hiring and background verification needs.",
        'services': "We offer a range of services including Crime Check, Drug Test, Driving Licence, Address Check, Face Verification, PAN Verification, Degree Verification, Employment Verification, Financial Integrity Check, Aadhar Verification, Passport Verification, Every Background Check.",
        'blockchain': "We leverage blockchain technology for the creation of offer letters and employment verification. When a company utilizes our offer portal to generate offer letters, it gains visibility into the number of current offer letters held by a candidate. This preemptive insight enables the company to discern whether the candidate is genuinely committed to joining or simply engaging in offer shopping. Additionally, during the verification of a candidate's past employment, if their previous companies have already validated the employment details, the new company can streamline the verification process, saving valuable time and resources that would otherwise be spent on re-verifying each past employer.",
        'why hirestar.io': "In the ever-evolving landscape of IT talent acquisition, Hirestar.io offers a refreshing solution. Traditional background verification can be slow, expensive, and prone to fraudulent activities. In response, we redefine the hiring experience with state-of-the-art solutions, ensuring expeditious, cost-effective, and highly secure vetting processes.",
        'what is hirestar.io': "Hirestar.io is a blockchain-powered background verification company offering a product known as the Self Verification Portal. This portal enables users to swiftly verify their identities, requiring only a few moments for the entire process. The features of the portal include multi-language support, ensuring accessibility for anyone familiar with smartphone usage. With an excellent user interface and user experience, the portal facilitates the verification of various ID cards, including Aadhar card, PAN card, and driving license. Additionally, it supports face verification, crime checks, and degree verification.",
        'language': "Experience the power of multi-language support, making it accessible to anyone with a smartphone. Now, language is no barrier; verification becomes effortless for users worldwide. Verify crucial documents like Aadhar card, PAN card, driving license, and more, effortlessly and in your preferred language",
        'what is blockchain technology': "Blockchain technology is a decentralized digital ledger that records transactions across multiple computers. These records are called \"blocks,\" and each block is linked to the previous one, forming a \"chain.\"",
        'how do you manage risk': "Managing risk is crucial in the hiring process. At Hirestar.io, we offer comprehensive background checks, including criminal records, drug tests, driving license verification, and financial integrity checks. Our blockchain-powered system ensures secure and tamper-proof verification, reducing the risk of hiring individuals with a history of fraudulent or unethical behavior.",
        'why did you choose blockchain technology': "Blockchain verification offers heightened security compared to traditional methods due to its features. Immutability ensures data integrity, making it nearly impervious to tampering. Decentralization reduces vulnerabilities associated with centralized systems, enhancing security. Additionally, encryption techniques protect data privacy, ensuring sensitive information remains confidential.",
        'Hirestar API': "Our API allows seamless integration with your existing systems. With comprehensive documentation and dedicated support, integrating Hirestar.io into your workflow becomes a hassle-free process. The API ensures efficient and secure data exchange, enabling you to leverage our background verification services effortlessly.",
        'products': "We offer a comprehensive range of products for thorough background verification. These include the Self Verification Portal, Employment Verification, Degree Verification, Crime Check, Drug Test, Driving Licence Check, Address Check, Face Verification, PAN Verification, Financial Integrity Check, Aadhar Verification, and Passport Verification. Our solutions are designed to meet diverse verification needs.",
        'identity verification': "Identity verification is a crucial process that ensures the security and trustworthiness of individuals in various transactions. It confirms that claimed identities match the information on file, enhancing security and compliance with regulations like KYC and AML.Identity verification involves confirming individuals' claimed identities through government-issued IDs, biometric data, or credentials. It's essential for mitigating fraud, identity theft, and ensuring regulatory compliance.",
        'degree verification' : "Degree verification ensures the authenticity of individuals' educational qualifications by verifying details like institution attended, dates of enrollment, graduation, and credentials earned.Employers and academic institutions use degree verification to confirm academic degrees, diplomas, or certifications. It's crucial for making informed decisions about employment and education.",
        'employment verification': "Employment verification is critical for confirming work history, job titles, duties, and reasons for leaving. It helps employers make informed hiring decisions and ensures compliance with background check requirements.Employers verify employment details like dates of employment, job roles, and salary information to validate candidates' qualifications and suitability for roles.",
        'financial integrity checks': "Financial integrity checks ensure transparency and reliability in financial activities. They detect irregularities, errors, or fraud to safeguard assets and maintain financial credibility.Organizations conduct financial integrity checks to uphold honesty and mitigate risks associated with financial misconduct or mismanagement.",
        'crime check verification': "Crime check verification involves thorough background checks to identify any criminal history or legal issues. It searches databases, court records, and law enforcement records for arrests, convictions, or charges.Employers use crime check verification to ensure safety and mitigate risks associated with hiring individuals with criminal backgrounds.",
        'Experience and Employee Background Verification powered by Blockchain': "Experience and Employee Background Verification powered by Blockchain ensures secure and efficient vetting processes. It leverages blockchain's immutability, transparency, and decentralization to verify employment history, qualifications, and credentials accurately. This innovative approach enhances trust and minimizes the risk of fraudulent activities.",
        'blockchain technology enhance the verification process': "Blockchain technology enhances the verification process by providing a secure and transparent decentralized ledger. It ensures the integrity and immutability of data, making it tamper-resistant. Through smart contracts and consensus mechanisms, blockchain establishes trust in the verification process, reducing the risk of fraud or manipulation.",
        'blockchain verification more secure than traditional methods': "Blockchain verification offers heightened security compared to traditional methods due to its features. Immutability ensures data integrity, making it nearly impervious to tampering. Decentralization reduces vulnerabilities associated with centralized systems, enhancing security. Additionally, encryption techniques protect data privacy, ensuring sensitive information remains confidential.",
        'types of employee information can be verified using this service': "Our service allows verification of a wide range of employee information, including educational qualifications, employment history, criminal records, financial integrity, identity documents (such as Aadhar card, PAN card, and passport), address details, and professional licenses. This comprehensive approach ensures thorough and reliable background checks.",
        'time taken for verification process': "The time taken for the verification process can vary based on the type of check and the specific requirements. However, our blockchain-powered verification system is designed to be efficient, often significantly reducing the time compared to traditional methods. For instance, some verifications can be completed within minutes, while others may take a few days.",
        'accessibility of information stored on the block chain': "Information stored on the blockchain is accessible to authorized parties only, ensuring data privacy and security. Access is controlled through encryption and permissioned blockchain networks, allowing only verified entities to view and verify the information. This ensures that sensitive data remains protected while maintaining transparency and trust in the verification process.",
        'transparency and trust': "Blockchain technology inherently provides transparency and trust in the verification process. Every transaction and data entry is recorded on an immutable ledger, accessible to authorized parties. This transparency ensures that all stakeholders have a clear view of the verification steps, fostering trust and confidence in the accuracy and integrity of the information.",
        'thanks': "You're welcome! If you have any other questions, feel free to ask.",
        'goodbye': "Goodbye! Have a great day!",
        'affirmation':"Great! How can I assist you further?",
        'negation':  "Alright.You can ask me any question's at anytime.I'm here to help",
        'confusion':"I'm here to help! Could you please provide more details or ask your question in a different way?",
        'small talk':"Fine,I'm here to help you! How can I assist you today?",
        'dissatisfaction': "I'm sorry to hear that you're not satisfied with my response. Could you please provide more details so I can better assist you?",
        'completion': "Thank you for using our services. If you have any more questions in the future, feel free to reach out. Have a great day!",
        'default': "I am sorry. I don't understand you. Could you please rephrase your question?",
  
    }
    return responses.get(intent, responses['default'])

@app.route('/chat', methods=['POST'])
def chat():
    if request.method == 'POST':
        user_message = request.json.get('message')
        if user_message:
            intent = classify_intent(user_message)
            response = generate_response(intent)
            return jsonify({'response': response})
        return jsonify({'response': 'No message received'})
    else:
        return jsonify({'response': 'Method not allowed'}), 405

if __name__ == '__main__':
    app.run(debug=True)
