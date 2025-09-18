"""Translation service using argostranslate."""

import logging
import argostranslate.package
import argostranslate.translate

logger = logging.getLogger(__name__)

# Language code mapping
LANGUAGE_MAP = {
    "en": "en",
    "pt": "pt", 
    "es": "es",
    "fr": "fr",
    "de": "de",
    "it": "it",
    "ru": "ru",
    "ja": "ja",
    "ko": "ko",
    "zh": "zh",
    "ar": "ar",
    "hi": "hi",
}

def ensure_translation_package(from_lang: str, to_lang: str) -> bool:
    """Ensure the translation package is installed."""
    try:
        # Check if package is already installed
        installed_packages = argostranslate.package.get_installed_packages()
        for package in installed_packages:
            if package.from_code == from_lang and package.to_code == to_lang:
                logger.info(f"Translation package {from_lang}->{to_lang} already installed")
                return True
        
        # Try to install from available packages
        available_packages = argostranslate.package.get_available_packages()
        target_package = None
        
        for package in available_packages:
            if package.from_code == from_lang and package.to_code == to_lang:
                target_package = package
                break
        
        if target_package:
            logger.info(f"Installing translation package {from_lang}->{to_lang}")
            argostranslate.package.install_from_path(target_package.download())
            return True
        else:
            logger.warning(f"Translation package {from_lang}->{to_lang} not available")
            return False
            
    except Exception as e:
        logger.error(f"Error ensuring translation package {from_lang}->{to_lang}: {e}")
        return False


def translate_text(text: str, source_lang: str = "en", target_lang: str = "pt") -> str:
    """Translate text from source language to target language using argostranslate."""
    try:
        # Map language codes
        source = LANGUAGE_MAP.get(source_lang, source_lang)
        target = LANGUAGE_MAP.get(target_lang, target_lang)
        
        logger.info(f"Translating from {source} to {target}: '{text[:100]}...'")
        
        # Skip translation if source and target are the same
        if source == target:
            logger.info("Source and target languages are the same, skipping translation")
            return text
        
        # Ensure translation package is available
        if not ensure_translation_package(source, target):
            logger.warning(f"Translation package not available for {source}->{target}, using fallback")
            # Fallback to simple dictionary for common words
            return _fallback_translate(text, source, target)
        
        # Perform translation using argostranslate
        translated_text = argostranslate.translate.translate(text, source, target)
        
        if translated_text and translated_text.strip():
            logger.info(f"Translation successful: '{text[:50]}...' -> '{translated_text[:50]}...'")
            return translated_text
        else:
            logger.warning("Empty translation result, using fallback")
            return _fallback_translate(text, source, target)
            
    except Exception as e:
        logger.error(f"Translation failed: {e}, using fallback")
        return _fallback_translate(text, source, target)


def _fallback_translate(text: str, source_lang: str, target_lang: str) -> str:
    """Fallback translation using simple dictionary."""
    if source_lang == "en" and target_lang == "pt":
        # Comprehensive English to Portuguese dictionary
        simple_translations = {
            # Greetings and basic phrases
            "hello": "olá",
            "hi": "oi", 
            "how are you": "como vai você",
            "good morning": "bom dia",
            "good afternoon": "boa tarde", 
            "good evening": "boa noite",
            "good night": "boa noite",
            "thank you": "obrigado",
            "thanks": "obrigado",
            "yes": "sim",
            "no": "não",
            "please": "por favor",
            "excuse me": "com licença",
            "sorry": "desculpe",
            "goodbye": "tchau",
            "see you": "até logo",
            "see you later": "até mais tarde",
            "nice to meet you": "prazer em conhecê-lo",
            
            # Pronouns and basic verbs
            "i am": "eu sou",
            "you are": "você é",
            "he is": "ele é",
            "she is": "ela é",
            "we are": "nós somos",
            "they are": "eles são",
            "i have": "eu tenho",
            "you have": "você tem",
            "he has": "ele tem",
            "she has": "ela tem",
            "we have": "nós temos",
            "they have": "eles têm",
            "i": "eu",
            "you": "você",
            "he": "ele",
            "she": "ela",
            "we": "nós",
            "they": "eles",
            "me": "me",
            "my": "meu",
            "your": "seu",
            "his": "dele",
            "her": "dela",
            "our": "nosso",
            "their": "deles",
            
            # Common verbs
            "am": "sou",
            "is": "é",
            "are": "são",
            "was": "era",
            "were": "eram",
            "be": "ser",
            "have": "ter",
            "has": "tem",
            "had": "tinha",
            "do": "fazer",
            "does": "faz",
            "did": "fez",
            "will": "vai",
            "would": "iria",
            "can": "pode",
            "could": "poderia",
            "should": "deveria",
            "must": "deve",
            "go": "ir",
            "come": "vir",
            "see": "ver",
            "know": "saber",
            "think": "pensar",
            "want": "querer",
            "need": "precisar",
            "like": "gostar",
            "love": "amar",
            "eat": "comer",
            "drink": "beber",
            "sleep": "dormir",
            "work": "trabalhar",
            "study": "estudar",
            "play": "jogar",
            "walk": "caminhar",
            "run": "correr",
            "speak": "falar",
            "talk": "conversar",
            "listen": "escutar",
            "read": "ler",
            "write": "escrever",
            "help": "ajudar",
            "give": "dar",
            "take": "pegar",
            "get": "conseguir",
            "make": "fazer",
            "put": "colocar",
            "find": "encontrar",
            "look": "olhar",
            "feel": "sentir",
            "tell": "contar",
            "say": "dizer",
            "ask": "perguntar",
            "answer": "responder",
            
            # Question words
            "what": "o que",
            "where": "onde",
            "when": "quando",
            "why": "por que",
            "how": "como",
            "who": "quem",
            "which": "qual",
            "whose": "de quem",
            
            # Time expressions
            "today": "hoje",
            "tomorrow": "amanhã",
            "yesterday": "ontem",
            "now": "agora",
            "later": "mais tarde",
            "before": "antes",
            "after": "depois",
            "always": "sempre",
            "never": "nunca",
            "sometimes": "às vezes",
            "often": "frequentemente",
            "usually": "geralmente",
            
            # Place expressions
            "here": "aqui",
            "there": "lá",
            "everywhere": "em todo lugar",
            "somewhere": "em algum lugar",
            "nowhere": "em lugar nenhum",
            "home": "casa",
            "work": "trabalho",
            "school": "escola",
            "hospital": "hospital",
            "restaurant": "restaurante",
            "store": "loja",
            "market": "mercado",
            
            # Adjectives
            "good": "bom",
            "bad": "ruim",
            "great": "ótimo",
            "excellent": "excelente",
            "wonderful": "maravilhoso",
            "beautiful": "bonito",
            "ugly": "feio",
            "nice": "legal",
            "fine": "bem",
            "ok": "ok",
            "okay": "ok",
            "big": "grande",
            "small": "pequeno",
            "large": "grande",
            "little": "pequeno",
            "new": "novo",
            "old": "velho",
            "young": "jovem",
            "hot": "quente",
            "cold": "frio",
            "warm": "morno",
            "cool": "fresco",
            "fast": "rápido",
            "slow": "lento",
            "easy": "fácil",
            "difficult": "difícil",
            "hard": "difícil",
            "soft": "macio",
            "happy": "feliz",
            "sad": "triste",
            "angry": "bravo",
            "tired": "cansado",
            "hungry": "com fome",
            "thirsty": "com sede",
            "sick": "doente",
            "healthy": "saudável",
            "rich": "rico",
            "poor": "pobre",
            "free": "grátis",
            "expensive": "caro",
            "cheap": "barato",
            "important": "importante",
            "interesting": "interessante",
            "boring": "chato",
            "funny": "engraçado",
            "serious": "sério",
            "different": "diferente",
            "same": "mesmo",
            "similar": "similar",
            "correct": "correto",
            "wrong": "errado",
            "right": "certo",
            "left": "esquerda",
            "true": "verdadeiro",
            "false": "falso",
            
            # Numbers
            "one": "um",
            "two": "dois",
            "three": "três",
            "four": "quatro",
            "five": "cinco",
            "six": "seis",
            "seven": "sete",
            "eight": "oito",
            "nine": "nove",
            "ten": "dez",
            "first": "primeiro",
            "second": "segundo",
            "third": "terceiro",
            "last": "último",
            
            # Common nouns
            "time": "tempo",
            "day": "dia",
            "night": "noite",
            "morning": "manhã",
            "afternoon": "tarde",
            "evening": "noite",
            "week": "semana",
            "month": "mês",
            "year": "ano",
            "hour": "hora",
            "minute": "minuto",
            "second": "segundo",
            "moment": "momento",
            "house": "casa",
            "car": "carro",
            "food": "comida",
            "water": "água",
            "money": "dinheiro",
            "friend": "amigo",
            "family": "família",
            "person": "pessoa",
            "people": "pessoas",
            "man": "homem",
            "woman": "mulher",
            "child": "criança",
            "children": "crianças",
            "boy": "menino",
            "girl": "menina",
            "baby": "bebê",
            "mother": "mãe",
            "father": "pai",
            "sister": "irmã",
            "brother": "irmão",
            "wife": "esposa",
            "husband": "marido",
            "son": "filho",
            "daughter": "filha",
            "love": "amor",
            "life": "vida",
            "world": "mundo",
            "country": "país",
            "city": "cidade",
            "place": "lugar",
            "street": "rua",
            "road": "estrada",
            "phone": "telefone",
            "computer": "computador",
            "book": "livro",
            "table": "mesa",
            "chair": "cadeira",
            "door": "porta",
            "window": "janela",
            "room": "quarto",
            "kitchen": "cozinha",
            "bathroom": "banheiro",
            "bed": "cama",
            "television": "televisão",
            "tv": "tv",
            "music": "música",
            "movie": "filme",
            "game": "jogo",
            "sport": "esporte",
            "dog": "cachorro",
            "cat": "gato",
            "animal": "animal",
            "tree": "árvore",
            "flower": "flor",
            "sun": "sol",
            "moon": "lua",
            "star": "estrela",
            "sky": "céu",
            "rain": "chuva",
            "snow": "neve",
            "wind": "vento",
            "fire": "fogo",
            "earth": "terra",
            "air": "ar",
            "color": "cor",
            "red": "vermelho",
            "blue": "azul",
            "green": "verde",
            "yellow": "amarelo",
            "black": "preto",
            "white": "branco",
            "problem": "problema",
            "question": "pergunta",
            "answer": "resposta",
            "idea": "ideia",
            "information": "informação",
            "news": "notícias",
            "story": "história",
            "example": "exemplo",
            "way": "caminho",
            "thing": "coisa",
            "something": "alguma coisa",
            "nothing": "nada",
            "everything": "tudo",
            "anything": "qualquer coisa",
            
            # Prepositions and connectors
            "and": "e",
            "or": "ou",
            "but": "mas",
            "because": "porque",
            "so": "então",
            "if": "se",
            "when": "quando",
            "while": "enquanto",
            "after": "depois",
            "before": "antes",
            "with": "com",
            "without": "sem",
            "for": "para",
            "to": "para",
            "from": "de",
            "of": "de",
            "in": "em",
            "on": "em",
            "at": "em",
            "by": "por",
            "about": "sobre",
            "under": "sob",
            "over": "sobre",
            "through": "através",
            "between": "entre",
            "during": "durante",
            "until": "até",
            "since": "desde",
            "against": "contra",
            "towards": "em direção a",
            "within": "dentro de",
            "outside": "fora",
            "inside": "dentro",
            "above": "acima",
            "below": "abaixo",
            "near": "perto",
            "far": "longe",
            "next": "próximo",
            "behind": "atrás",
            "front": "frente",
            "around": "ao redor",
            
            # Other common words
            "very": "muito",
            "more": "mais",
            "most": "mais",
            "less": "menos",
            "least": "menos",
            "much": "muito",
            "many": "muitos",
            "few": "poucos",
            "little": "pouco",
            "all": "todos",
            "some": "alguns",
            "any": "qualquer",
            "each": "cada",
            "every": "todo",
            "other": "outro",
            "another": "outro",
            "both": "ambos",
            "either": "qualquer um",
            "neither": "nem",
            "only": "apenas",
            "also": "também",
            "too": "também",
            "still": "ainda",
            "already": "já",
            "just": "apenas",
            "even": "mesmo",
            "maybe": "talvez",
            "perhaps": "talvez",
            "probably": "provavelmente",
            "certainly": "certamente",
            "definitely": "definitivamente",
            "absolutely": "absolutamente",
            "exactly": "exatamente",
            "completely": "completamente",
            "totally": "totalmente",
            "quite": "bastante",
            "rather": "bastante",
            "pretty": "bem",
            "enough": "suficiente",
            "almost": "quase",
            "nearly": "quase",
            "especially": "especialmente",
            "particularly": "particularmente",
            "really": "realmente",
            "actually": "na verdade",
            "finally": "finalmente",
            "suddenly": "de repente",
            "quickly": "rapidamente",
            "slowly": "lentamente",
            "carefully": "cuidadosamente",
            "easily": "facilmente",
            "clearly": "claramente",
            "certainly": "certamente",
            "obviously": "obviamente",
        }
        
        text_lower = text.lower()
        translated = text
        
        # Replace known words/phrases (order matters - longer phrases first)
        sorted_translations = sorted(simple_translations.items(), key=lambda x: len(x[0]), reverse=True)
        
        for en_word, pt_word in sorted_translations:
            if en_word in text_lower:
                # Case-insensitive replacement maintaining original case
                import re
                pattern = r'\b' + re.escape(en_word) + r'\b'
                translated = re.sub(pattern, pt_word, translated, flags=re.IGNORECASE)
        
        return translated
    
    # If no fallback available, return original
    return text


def initialize_translation_service() -> None:
    """Initialize translation service by updating package index."""
    try:
        logger.info("Initializing argostranslate translation service...")
        argostranslate.package.update_package_index()
        
        # Pre-install common language pairs
        common_pairs = [("en", "pt"), ("pt", "en"), ("en", "es"), ("es", "en")]
        for from_lang, to_lang in common_pairs:
            ensure_translation_package(from_lang, to_lang)
        
        logger.info("Translation service initialized successfully")
            
    except Exception as e:
        logger.error(f"Error initializing translation service: {e}")
        logger.info("Translation service will use fallback dictionary")
