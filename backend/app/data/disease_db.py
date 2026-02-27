"""
FasalDrishti - Comprehensive Crop Disease Database
Contains disease info, treatments, and prevention tips for major Indian crops.
"""

DISEASE_DATABASE = {
    # ============ TOMATO DISEASES ============
    "tomato_early_blight": {
        "disease_name": "Early Blight",
        "hindi_name": "अगेती झुलसा",
        "scientific_name": "Alternaria solani",
        "crop": "Tomato",
        "crop_hindi": "टमाटर",
        "category": "Fungal",
        "severity_typical": "moderate",
        "description": "Dark brown to black spots with concentric rings (target-like pattern) appearing first on older lower leaves. Spots may coalesce and cause leaf drop.",
        "description_hindi": "गहरे भूरे से काले धब्बे जो संकेंद्रित वलयों (निशाने जैसा पैटर्न) के साथ पहले पुरानी निचली पत्तियों पर दिखाई देते हैं।",
        "symptoms": [
            "Dark spots with concentric rings on leaves",
            "Yellowing of leaves around spots",
            "Premature leaf drop starting from bottom",
            "Dark sunken spots on stems",
            "Fruit may show dark leathery spots at stem end"
        ],
        "treatments": [
            {
                "name": "Mancozeb 75% WP",
                "dosage": "2.5 grams per liter of water",
                "method": "Foliar spray",
                "frequency": "Every 7-10 days",
                "cost_per_acre": 180
            },
            {
                "name": "Chlorothalonil 75% WP",
                "dosage": "2 grams per liter of water",
                "method": "Foliar spray",
                "frequency": "Every 10-14 days",
                "cost_per_acre": 220
            },
            {
                "name": "Azoxystrobin 23% SC",
                "dosage": "1 ml per liter of water",
                "method": "Foliar spray",
                "frequency": "Every 14 days",
                "cost_per_acre": 350
            }
        ],
        "organic_treatments": [
            "Neem oil spray (5ml/L water)",
            "Trichoderma viride (4g/L water) as preventive",
            "Copper oxychloride 50% WP (3g/L water)"
        ],
        "prevention": [
            "Use disease-free certified seeds",
            "Practice 3-year crop rotation",
            "Remove and destroy infected plant debris",
            "Maintain proper plant spacing (60x45 cm)",
            "Avoid overhead irrigation",
            "Mulch around plants to prevent soil splash"
        ],
        "favorable_conditions": "Warm temperatures (24-29°C), high humidity, heavy dew, frequent rainfall",
        "image_keywords": ["concentric rings", "target spots", "brown spots", "leaf blight", "tomato"]
    },

    "tomato_late_blight": {
        "disease_name": "Late Blight",
        "hindi_name": "पछेती झुलसा",
        "scientific_name": "Phytophthora infestans",
        "crop": "Tomato",
        "crop_hindi": "टमाटर",
        "category": "Oomycete",
        "severity_typical": "severe",
        "description": "Water-soaked, pale green to brown spots that rapidly enlarge. White fuzzy growth appears on leaf undersides in humid conditions. Entire plant can collapse within days.",
        "description_hindi": "पानी में भीगे, हल्के हरे से भूरे धब्बे जो तेजी से बढ़ते हैं। नमी में पत्तियों की निचली सतह पर सफेद रोएंदार वृद्धि दिखती है।",
        "symptoms": [
            "Water-soaked grayish-green spots on leaves",
            "White mold growth on leaf undersides",
            "Dark brown to black lesions on stems",
            "Rapid wilting and death of entire plant",
            "Brown, firm rot on fruits"
        ],
        "treatments": [
            {
                "name": "Metalaxyl 8% + Mancozeb 64% WP",
                "dosage": "2.5 grams per liter",
                "method": "Foliar spray",
                "frequency": "Every 7 days during outbreak",
                "cost_per_acre": 320
            },
            {
                "name": "Cymoxanil 8% + Mancozeb 64% WP",
                "dosage": "3 grams per liter",
                "method": "Foliar spray",
                "frequency": "Every 7-10 days",
                "cost_per_acre": 290
            }
        ],
        "organic_treatments": [
            "Copper hydroxide 77% WP (2g/L)",
            "Bordeaux mixture (1%)",
            "Remove and burn all infected parts immediately"
        ],
        "prevention": [
            "Plant resistant varieties",
            "Avoid excess irrigation",
            "Ensure good air circulation",
            "Destroy volunteer tomato/potato plants",
            "Apply preventive fungicide before rainy season"
        ],
        "favorable_conditions": "Cool temperatures (15-22°C), high humidity (>90%), prolonged wet weather",
        "image_keywords": ["water soaked", "white mold", "rapid wilting", "dark lesions", "tomato"]
    },

    "tomato_leaf_curl": {
        "disease_name": "Tomato Leaf Curl Virus",
        "hindi_name": "टमाटर पत्ती मोड़क विषाणु",
        "scientific_name": "ToLCV (Begomovirus)",
        "crop": "Tomato",
        "crop_hindi": "टमाटर",
        "category": "Viral",
        "severity_typical": "severe",
        "description": "Leaves curl upward and inward, becoming thick and leathery. Plants become stunted with reduced fruit production. Spread by whiteflies.",
        "description_hindi": "पत्तियां ऊपर और अंदर की ओर मुड़ जाती हैं, मोटी और चमड़े जैसी हो जाती हैं। पौधे बौने हो जाते हैं।",
        "symptoms": [
            "Upward curling and cupping of leaves",
            "Leaves become thick and leathery",
            "Yellowing of leaf margins",
            "Stunted plant growth",
            "Drastic reduction in fruit set"
        ],
        "treatments": [
            {
                "name": "Imidacloprid 17.8% SL (for whitefly control)",
                "dosage": "0.3 ml per liter of water",
                "method": "Foliar spray",
                "frequency": "Every 15 days",
                "cost_per_acre": 150
            },
            {
                "name": "Thiamethoxam 25% WG",
                "dosage": "0.3 grams per liter",
                "method": "Foliar spray",
                "frequency": "Every 15 days",
                "cost_per_acre": 180
            }
        ],
        "organic_treatments": [
            "Yellow sticky traps for whitefly monitoring",
            "Neem oil 5ml/L spray every 7 days",
            "Remove and destroy infected plants"
        ],
        "prevention": [
            "Use ToLCV-resistant varieties (Arka Rakshak, etc.)",
            "Use insect-proof nursery nets",
            "Install yellow sticky traps",
            "Remove weeds that harbor whiteflies",
            "Seedling treatment with Imidacloprid"
        ],
        "favorable_conditions": "High whitefly population, warm dry weather, presence of alternate hosts",
        "image_keywords": ["leaf curl", "upward curling", "thick leaves", "stunted", "tomato"]
    },

    # ============ RICE DISEASES ============
    "rice_blast": {
        "disease_name": "Rice Blast",
        "hindi_name": "धान का ब्लास्ट",
        "scientific_name": "Magnaporthe oryzae",
        "crop": "Rice",
        "crop_hindi": "धान",
        "category": "Fungal",
        "severity_typical": "severe",
        "description": "Diamond-shaped or eye-shaped spots with gray centers and brown borders on leaves. Can also affect neck, nodes, and panicles causing severe yield loss.",
        "description_hindi": "पत्तियों पर हीरे या आंख के आकार के धब्बे जिनका केंद्र भूरा और किनारे भूरे होते हैं। गर्दन और बालियों को भी प्रभावित कर सकता है।",
        "symptoms": [
            "Diamond/eye-shaped spots on leaves",
            "Gray center with brown border",
            "Lesions on leaf collar, neck, and nodes",
            "Neck rot causing white/empty panicles",
            "Severe: entire leaf drying"
        ],
        "treatments": [
            {
                "name": "Tricyclazole 75% WP",
                "dosage": "0.6 grams per liter",
                "method": "Foliar spray",
                "frequency": "At disease onset, repeat after 15 days",
                "cost_per_acre": 280
            },
            {
                "name": "Isoprothiolane 40% EC",
                "dosage": "1.5 ml per liter",
                "method": "Foliar spray",
                "frequency": "Every 15 days",
                "cost_per_acre": 320
            },
            {
                "name": "Carbendazim 50% WP",
                "dosage": "1 gram per liter",
                "method": "Foliar spray",
                "frequency": "Every 10-15 days",
                "cost_per_acre": 150
            }
        ],
        "organic_treatments": [
            "Pseudomonas fluorescens (10g/L water)",
            "Silicon application for plant strengthening",
            "Avoid excess nitrogen application"
        ],
        "prevention": [
            "Use blast-resistant varieties",
            "Balanced fertilizer (avoid excess N)",
            "Maintain proper water management",
            "Seed treatment with Tricyclazole",
            "Avoid close spacing"
        ],
        "favorable_conditions": "High humidity (>90%), temperature 25-28°C, excess nitrogen, poor drainage",
        "image_keywords": ["diamond shaped", "eye shaped", "gray center", "leaf spots", "rice"]
    },

    "rice_brown_spot": {
        "disease_name": "Brown Spot",
        "hindi_name": "भूरा धब्बा रोग",
        "scientific_name": "Bipolaris oryzae",
        "crop": "Rice",
        "crop_hindi": "धान",
        "category": "Fungal",
        "severity_typical": "moderate",
        "description": "Oval to circular brown spots on leaves, often with a yellow halo. Associated with poor soil fertility and nutrient deficiency.",
        "description_hindi": "पत्तियों पर अंडाकार से गोलाकार भूरे धब्बे, अक्सर पीले घेरे के साथ। खराब मिट्टी की उर्वरता से जुड़ा है।",
        "symptoms": [
            "Oval brown spots on leaves",
            "Yellow halo around spots",
            "Spots on glumes causing discolored grain",
            "Seedling blight in nursery",
            "Associated with potassium deficiency"
        ],
        "treatments": [
            {
                "name": "Mancozeb 75% WP",
                "dosage": "2.5 grams per liter",
                "method": "Foliar spray",
                "frequency": "Every 10 days",
                "cost_per_acre": 180
            },
            {
                "name": "Edifenphos 50% EC",
                "dosage": "1 ml per liter",
                "method": "Foliar spray",
                "frequency": "Every 15 days",
                "cost_per_acre": 200
            }
        ],
        "organic_treatments": [
            "Apply potash fertilizer (MOP 50kg/ha)",
            "Pseudomonas fluorescens seed treatment",
            "FYM/compost application"
        ],
        "prevention": [
            "Balanced NPK fertilization",
            "Use certified disease-free seeds",
            "Seed treatment before sowing",
            "Adequate potassium application",
            "Proper water management"
        ],
        "favorable_conditions": "Poor soil, nutrient deficiency, high humidity, temperature 25-30°C",
        "image_keywords": ["brown spots", "oval spots", "yellow halo", "nutrient deficiency", "rice"]
    },

    # ============ WHEAT DISEASES ============
    "wheat_leaf_rust": {
        "disease_name": "Leaf Rust (Brown Rust)",
        "hindi_name": "पत्ती का रतुआ (भूरा रतुआ)",
        "scientific_name": "Puccinia triticina",
        "crop": "Wheat",
        "crop_hindi": "गेहूं",
        "category": "Fungal",
        "severity_typical": "severe",
        "description": "Small, round to oval, orange-brown pustules scattered randomly on upper leaf surface. Pustules release powdery orange spores when touched.",
        "description_hindi": "पत्ती की ऊपरी सतह पर छोटे, गोल से अंडाकार, नारंगी-भूरे फुंसी बिखरे होते हैं। छूने पर नारंगी पाउडर जैसे बीजाणु निकलते हैं।",
        "symptoms": [
            "Orange-brown pustules on leaf upper surface",
            "Random distribution of pustules",
            "Powdery spores released when touched",
            "Severe infection causes leaf drying",
            "Reduced grain filling"
        ],
        "treatments": [
            {
                "name": "Propiconazole 25% EC",
                "dosage": "1 ml per liter of water",
                "method": "Foliar spray",
                "frequency": "At first appearance, repeat after 15 days",
                "cost_per_acre": 250
            },
            {
                "name": "Tebuconazole 25.9% EC",
                "dosage": "1 ml per liter",
                "method": "Foliar spray",
                "frequency": "Once or twice at 15-day interval",
                "cost_per_acre": 280
            }
        ],
        "organic_treatments": [
            "Grow resistant varieties (primary defense)",
            "Timely sowing (avoid late sowing)",
            "Balanced nitrogen application"
        ],
        "prevention": [
            "Plant rust-resistant varieties",
            "Early sowing (November)",
            "Balanced nitrogen fertilization",
            "Avoid late irrigation",
            "Monitor fields from January onwards"
        ],
        "favorable_conditions": "Temperature 15-25°C, high humidity, dew, late-sown crop",
        "image_keywords": ["orange pustules", "brown rust", "rust spots", "powdery spores", "wheat"]
    },

    "wheat_yellow_rust": {
        "disease_name": "Yellow Rust (Stripe Rust)",
        "hindi_name": "पीला रतुआ (धारी रतुआ)",
        "scientific_name": "Puccinia striiformis",
        "crop": "Wheat",
        "crop_hindi": "गेहूं",
        "category": "Fungal",
        "severity_typical": "severe",
        "description": "Yellow-orange pustules arranged in stripes along leaf veins. More damaging than brown rust, can cause complete crop failure.",
        "description_hindi": "पत्ती की नसों के साथ धारियों में व्यवस्थित पीले-नारंगी फुंसी। भूरे रतुआ से अधिक हानिकारक।",
        "symptoms": [
            "Yellow-orange pustules in stripes along veins",
            "Stripes on leaves, leaf sheaths, and awns",
            "Severe yellowing and drying of leaves",
            "Shriveled grains",
            "Complete crop failure in severe cases"
        ],
        "treatments": [
            {
                "name": "Propiconazole 25% EC",
                "dosage": "1 ml per liter",
                "method": "Foliar spray",
                "frequency": "Immediately at first sign",
                "cost_per_acre": 250
            },
            {
                "name": "Triadimefon 25% WP",
                "dosage": "1 gram per liter",
                "method": "Foliar spray",
                "frequency": "Every 15 days",
                "cost_per_acre": 200
            }
        ],
        "organic_treatments": [
            "Use resistant varieties (best strategy)",
            "Early sowing to escape infection",
            "Balanced fertilization"
        ],
        "prevention": [
            "Plant resistant varieties (critical)",
            "Early sowing",
            "Avoid excess nitrogen",
            "Report to agriculture department immediately",
            "Destroy volunteer wheat plants"
        ],
        "favorable_conditions": "Cool temperature (10-15°C), humidity, cloudy weather, north Indian plains in Jan-Feb",
        "image_keywords": ["yellow stripes", "stripe rust", "yellow pustules", "parallel lines", "wheat"]
    },

    # ============ COTTON DISEASES ============
    "cotton_bacterial_blight": {
        "disease_name": "Bacterial Blight",
        "hindi_name": "जीवाणु अंगमारी",
        "scientific_name": "Xanthomonas citri pv. malvacearum",
        "crop": "Cotton",
        "crop_hindi": "कपास",
        "category": "Bacterial",
        "severity_typical": "moderate",
        "description": "Angular water-soaked spots on leaves that turn brown-black. Lesions are vein-limited giving angular appearance. Black arm symptoms on stems.",
        "description_hindi": "पत्तियों पर कोणीय पानी में भीगे धब्बे जो भूरे-काले हो जाते हैं। तनों पर काली भुजा के लक्षण।",
        "symptoms": [
            "Angular water-soaked leaf spots",
            "Spots turn brown to black",
            "Vein-limited lesions",
            "Black arm on stems and branches",
            "Boll rot in severe cases"
        ],
        "treatments": [
            {
                "name": "Streptocycline + Copper Oxychloride",
                "dosage": "0.5g Streptocycline + 3g COC per liter",
                "method": "Foliar spray",
                "frequency": "Every 10-15 days",
                "cost_per_acre": 200
            },
            {
                "name": "Copper Hydroxide 77% WP",
                "dosage": "2 grams per liter",
                "method": "Foliar spray",
                "frequency": "Every 10 days",
                "cost_per_acre": 180
            }
        ],
        "organic_treatments": [
            "Seed treatment with Pseudomonas fluorescens",
            "Acid delinting of seeds",
            "Copper-based sprays"
        ],
        "prevention": [
            "Use disease-free certified seeds",
            "Acid delinting of seeds",
            "Seed treatment with antibiotics",
            "Avoid excess irrigation during vegetative stage",
            "Remove and destroy infected plant debris"
        ],
        "favorable_conditions": "Warm (25-35°C), humid, rainy weather, sprinkler irrigation",
        "image_keywords": ["angular spots", "water soaked", "black arm", "vein limited", "cotton"]
    },

    # ============ POTATO DISEASES ============
    "potato_late_blight": {
        "disease_name": "Late Blight",
        "hindi_name": "पछेती झुलसा",
        "scientific_name": "Phytophthora infestans",
        "crop": "Potato",
        "crop_hindi": "आलू",
        "category": "Oomycete",
        "severity_typical": "severe",
        "description": "Water-soaked spots on leaf tips and edges that rapidly turn dark brown. White mold on undersides. Tubers develop firm brown rot.",
        "description_hindi": "पत्ती के किनारों पर पानी में भीगे धब्बे जो तेजी से गहरे भूरे हो जाते हैं। कंदों में सड़न होती है।",
        "symptoms": [
            "Water-soaked spots on leaf tips and margins",
            "Rapid browning and blackening",
            "White cottony growth on leaf undersides",
            "Entire plant collapse in 3-5 days",
            "Firm granular brown rot in tubers"
        ],
        "treatments": [
            {
                "name": "Metalaxyl 8% + Mancozeb 64% WP",
                "dosage": "2.5 grams per liter",
                "method": "Foliar spray",
                "frequency": "Every 7 days during outbreak",
                "cost_per_acre": 350
            },
            {
                "name": "Cymoxanil 8% + Mancozeb 64% WP",
                "dosage": "3 grams per liter",
                "method": "Foliar spray",
                "frequency": "Every 7-10 days",
                "cost_per_acre": 300
            },
            {
                "name": "Dimethomorph 50% WP",
                "dosage": "1 gram per liter",
                "method": "Foliar spray",
                "frequency": "Every 7 days",
                "cost_per_acre": 400
            }
        ],
        "organic_treatments": [
            "Bordeaux mixture 1%",
            "Copper hydroxide spray",
            "Remove and burn all infected plants"
        ],
        "prevention": [
            "Plant certified disease-free tubers",
            "Use resistant varieties (Kufri Jyoti, etc.)",
            "Proper hilling up of tubers",
            "Preventive spray before weather turns cold and humid",
            "Good drainage, avoid waterlogging"
        ],
        "favorable_conditions": "Cool nights (10-15°C), humid days, fog, continuous rain",
        "image_keywords": ["water soaked", "white mold", "rapid browning", "tuber rot", "potato"]
    },

    # ============ CHILI DISEASES ============
    "chili_anthracnose": {
        "disease_name": "Anthracnose / Fruit Rot",
        "hindi_name": "एंथ्रेक्नोज / फल सड़न",
        "scientific_name": "Colletotrichum capsici",
        "crop": "Chili",
        "crop_hindi": "मिर्च",
        "category": "Fungal",
        "severity_typical": "severe",
        "description": "Small circular sunken spots on ripe fruits that enlarge and develop dark concentric rings. Fruits shrivel and dry up (die-back on twigs).",
        "description_hindi": "पके फलों पर छोटे गोलाकार धंसे हुए धब्बे जो बड़े होकर गहरे संकेंद्रित वलय बनाते हैं। फल सूख जाते हैं।",
        "symptoms": [
            "Sunken circular spots on fruits",
            "Dark spots with concentric rings",
            "Fruits shrivel and mummify",
            "Die-back of twigs from tips",
            "Seeds in infected fruits turn black"
        ],
        "treatments": [
            {
                "name": "Carbendazim 50% WP",
                "dosage": "1 gram per liter",
                "method": "Foliar spray",
                "frequency": "Every 10-15 days",
                "cost_per_acre": 150
            },
            {
                "name": "Mancozeb 75% WP + Carbendazim 50% WP",
                "dosage": "2g Mancozeb + 1g Carbendazim per liter",
                "method": "Foliar spray alternately",
                "frequency": "Every 10 days",
                "cost_per_acre": 200
            }
        ],
        "organic_treatments": [
            "Trichoderma viride seed treatment (4g/kg)",
            "Neem oil spray 5ml/L",
            "Hot water seed treatment (52°C for 30 min)"
        ],
        "prevention": [
            "Use disease-free seeds",
            "Seed treatment before sowing",
            "Practice crop rotation (3 years)",
            "Avoid excess irrigation during fruiting",
            "Harvest ripe fruits promptly"
        ],
        "favorable_conditions": "Warm (28-32°C), high humidity, rainy season, dense planting",
        "image_keywords": ["sunken spots", "fruit rot", "concentric rings", "shriveled fruit", "chili"]
    },

    # ============ ONION DISEASES ============
    "onion_purple_blotch": {
        "disease_name": "Purple Blotch",
        "hindi_name": "बैंगनी धब्बा रोग",
        "scientific_name": "Alternaria porri",
        "crop": "Onion",
        "crop_hindi": "प्याज",
        "category": "Fungal",
        "severity_typical": "moderate",
        "description": "Purple-brown lesions with concentric zones on leaves. Lesions start as small water-soaked spots and enlarge. Heavily affected leaves dry up.",
        "description_hindi": "पत्तियों पर बैंगनी-भूरे धब्बे जिनमें संकेंद्रित क्षेत्र होते हैं। प्रभावित पत्तियां सूख जाती हैं।",
        "symptoms": [
            "Purple-brown oval lesions on leaves",
            "Concentric zonation in lesions",
            "Initial water-soaked spots",
            "Drying and collapse of leaves",
            "Neck infection during storage"
        ],
        "treatments": [
            {
                "name": "Mancozeb 75% WP",
                "dosage": "2.5 grams per liter",
                "method": "Foliar spray with sticker",
                "frequency": "Every 10 days",
                "cost_per_acre": 180
            },
            {
                "name": "Tebuconazole 25.9% EC",
                "dosage": "1 ml per liter",
                "method": "Foliar spray",
                "frequency": "Every 15 days",
                "cost_per_acre": 280
            }
        ],
        "organic_treatments": [
            "Copper oxychloride 50% WP (3g/L)",
            "Neem oil spray",
            "Trichoderma soil application"
        ],
        "prevention": [
            "Use healthy planting material",
            "Proper plant spacing",
            "Avoid overhead irrigation",
            "Remove crop debris after harvest",
            "Store onions in dry, ventilated place"
        ],
        "favorable_conditions": "High humidity (>80%), warm temperature (25-30°C), rainfall",
        "image_keywords": ["purple lesions", "concentric zones", "brown spots", "leaf drying", "onion"]
    },

    # ============ HEALTHY PLANT ============
    "healthy": {
        "disease_name": "Healthy Plant",
        "hindi_name": "स्वस्थ पौधा",
        "scientific_name": "N/A",
        "crop": "General",
        "crop_hindi": "सामान्य",
        "category": "Healthy",
        "severity_typical": "none",
        "description": "No disease detected. The plant appears healthy with normal green coloration and no visible symptoms of infection.",
        "description_hindi": "कोई बीमारी नहीं पाई गई। पौधा सामान्य हरे रंग और बिना किसी संक्रमण के लक्षणों के साथ स्वस्थ दिखाई देता है।",
        "symptoms": ["No symptoms - plant appears healthy"],
        "treatments": [
            {
                "name": "Regular monitoring",
                "dosage": "N/A",
                "method": "Visual inspection",
                "frequency": "Weekly",
                "cost_per_acre": 0
            }
        ],
        "organic_treatments": [
            "Continue good agricultural practices",
            "Regular crop monitoring",
            "Balanced nutrition"
        ],
        "prevention": [
            "Continue regular field monitoring",
            "Maintain balanced fertilizer schedule",
            "Proper irrigation management",
            "Timely weed management",
            "Monitor for early signs of pest/disease"
        ],
        "favorable_conditions": "N/A",
        "image_keywords": ["healthy", "green", "normal", "no spots", "clean"]
    }
}

# Crop-wise disease mapping for quick lookup
CROP_DISEASES = {
    "tomato": ["tomato_early_blight", "tomato_late_blight", "tomato_leaf_curl"],
    "rice": ["rice_blast", "rice_brown_spot"],
    "wheat": ["wheat_leaf_rust", "wheat_yellow_rust"],
    "cotton": ["cotton_bacterial_blight"],
    "potato": ["potato_late_blight"],
    "chili": ["chili_anthracnose"],
    "onion": ["onion_purple_blotch"],
}

# All supported crops
SUPPORTED_CROPS = list(CROP_DISEASES.keys())

# Language mapping for responses
LANGUAGE_MAP = {
    "en": "English",
    "hi": "Hindi",
    "ta": "Tamil",
    "te": "Telugu",
    "kn": "Kannada",
    "mr": "Marathi",
    "bn": "Bengali",
    "gu": "Gujarati",
    "pa": "Punjabi",
    "or": "Odia",
    "ml": "Malayalam",
    "as": "Assamese",
}
