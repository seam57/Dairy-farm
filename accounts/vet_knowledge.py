"""
Livestock Pro — Veterinary Knowledge Base
==========================================
এই file-এ বাংলাদেশের গবাদি পশুর সাধারণ রোগ, লক্ষণ ও চিকিৎসার তথ্য আছে।
RAG system এই knowledge base থেকে relevant তথ্য খুঁজে AI-কে দেবে।
"""

VETERINARY_KNOWLEDGE = [

    # ═══════════════════════════════════════
    # গরু — Cattle Diseases
    # ═══════════════════════════════════════
    {
        "id": "cow_fmd",
        "title": "গরুর খুরারোগ (Foot and Mouth Disease - FMD)",
        "animal": "গরু",
        "category": "ভাইরাসজনিত রোগ",
        "symptoms": "মুখে ও পায়ের খুরে ঘা, জ্বর ১০৪-১০৬°F, লালা ঝরা, খাওয়া বন্ধ, খোঁড়ানো, দুধ উৎপাদন কমে যাওয়া",
        "treatment": "আক্রান্ত স্থানে পটাসিয়াম পারম্যাঙ্গানেট দিয়ে ধোয়া, Terramycin মলম লাগানো, জ্বরের জন্য Paracetamol, ভেটেরিনারি ডাক্তারের পরামর্শ নেওয়া",
        "prevention": "FMD vaccine বছরে ২ বার দেওয়া, আক্রান্ত পশু আলাদা রাখা, জীবাণুনাশক দিয়ে খোঁয়াড় পরিষ্কার",
        "vaccine": "FMD Vaccine (বছরে ২ বার), প্রথম dose ৩ মাস বয়সে",
        "urgency": "জরুরি — সংক্রামক রোগ, দ্রুত ডাক্তার ডাকুন",
        "keywords": "খুরারোগ fmd মুখে ঘা পায়ে ঘা লালা ঝরা খোঁড়ানো জ্বর দুধ কম"
    },
    {
        "id": "cow_anthrax",
        "title": "গরুর তড়কা রোগ (Anthrax)",
        "animal": "গরু",
        "category": "ব্যাকটেরিয়াজনিত রোগ",
        "symptoms": "হঠাৎ মৃত্যু, উচ্চ জ্বর ১০৭°F, শরীর কাঁপা, নাক-মুখ-পায়ুপথ দিয়ে কালো রক্ত, পেট ফোলা",
        "treatment": "Penicillin injection অবিলম্বে, Anthrax antiserum, ভেটেরিনারি ডাক্তারের জরুরি সাহায্য নিন",
        "prevention": "Anthrax vaccine বছরে একবার, মৃত পশু পুড়িয়ে বা গভীরে পুঁতে ফেলা",
        "vaccine": "Anthrax Spore Vaccine (বছরে ১ বার)",
        "urgency": "অত্যন্ত জরুরি — মানুষের জন্যও বিপজ্জনক",
        "keywords": "তড়কা anthrax হঠাৎ মৃত্যু কালো রক্ত পেট ফোলা জরুরি"
    },
    {
        "id": "cow_hs",
        "title": "গলাফুলা রোগ (Haemorrhagic Septicaemia - HS)",
        "animal": "গরু ও মহিষ",
        "category": "ব্যাকটেরিয়াজনিত রোগ",
        "symptoms": "গলা ও বুক ফুলে যাওয়া, উচ্চ জ্বর, শ্বাসকষ্ট, লালা ঝরা, দুর্বলতা, মৃত্যু ২৪-৩৬ ঘণ্টায়",
        "treatment": "Oxytetracycline injection, Sulphonamide, জরুরি ভেটেরিনারি সেবা",
        "prevention": "HS vaccine বছরে ২ বার, বর্ষার আগে অবশ্যই",
        "vaccine": "HS Vaccine (বছরে ২ বার — মে ও নভেম্বর)",
        "urgency": "অত্যন্ত জরুরি — ২৪ ঘণ্টায় মৃত্যু হতে পারে",
        "keywords": "গলাফুলা hs গলা ফোলা শ্বাসকষ্ট জ্বর দুর্বলতা"
    },
    {
        "id": "cow_milk_fever",
        "title": "দুধ জ্বর (Milk Fever)",
        "animal": "গরু",
        "category": "পুষ্টিজনিত সমস্যা",
        "symptoms": "প্রসবের পর ১-৩ দিনে দুর্বলতা, শুয়ে পড়া, ঘাড় বাঁকানো, ঠান্ডা কান ও পা, চেতনা হারানো",
        "treatment": "Calcium borogluconate IV injection অবিলম্বে, ভেটেরিনারি ডাক্তার ডাকুন",
        "prevention": "গর্ভাবস্থায় সুষম খাবার, Calcium supplement, প্রসবের আগে কম ক্যালসিয়াম খাদ্য",
        "vaccine": "নেই, প্রতিরোধই মূল উপায়",
        "urgency": "জরুরি — দ্রুত চিকিৎসা না হলে মৃত্যু",
        "keywords": "দুধ জ্বর milk fever প্রসব পরবর্তী দুর্বলতা শুয়ে পড়া ঘাড় বাঁকা ক্যালসিয়াম"
    },
    {
        "id": "cow_mastitis",
        "title": "ওলান প্রদাহ (Mastitis)",
        "animal": "গরু",
        "category": "ব্যাকটেরিয়াজনিত রোগ",
        "symptoms": "ওলান ফোলা ও লাল, দুধে রক্ত বা পুঁজ, দুধ কম, ছোঁয়া লাগলে ব্যথা, জ্বর",
        "treatment": "Intramammary antibiotic (Amoxicillin), Oxytocin injection, দিনে ৪-৫ বার দুধ দোহানো, ওলান গরম সেঁক",
        "prevention": "দোহানোর আগে ও পরে ওলান পরিষ্কার, Teat dipping, পরিষ্কার পরিবেশ",
        "vaccine": "নেই",
        "urgency": "মাঝারি — দ্রুত চিকিৎসায় ভালো হয়",
        "keywords": "mastitis ওলান প্রদাহ দুধে রক্ত পুঁজ ওলান ফোলা দুধ কম"
    },
    {
        "id": "cow_bloat",
        "title": "পেট ফাঁপা (Bloat / Tympany)",
        "animal": "গরু ও ছাগল",
        "category": "পরিপাক সমস্যা",
        "symptoms": "পেটের বাম দিক ফুলে যাওয়া, শ্বাসকষ্ট, অস্থিরতা, খাওয়া বন্ধ, পা দিয়ে পেটে লাথি",
        "treatment": "Trocar দিয়ে গ্যাস বের করা, Bloat remedy (Turpentine oil + vegetable oil), হাঁটানো, ভেটেরিনারি সাহায্য",
        "prevention": "ভেজা ঘাস একসাথে বেশি না খাওয়ানো, ধীরে ধীরে নতুন খাবারে অভ্যস্ত করা",
        "vaccine": "নেই",
        "urgency": "জরুরি — দ্রুত চিকিৎসা না হলে মৃত্যু",
        "keywords": "পেট ফাঁপা bloat tympany পেট ফোলা বাম পাশ শ্বাসকষ্ট গ্যাস"
    },
    {
        "id": "cow_worm",
        "title": "গরুর কৃমি সংক্রমণ (Helminthiasis)",
        "animal": "গরু",
        "category": "পরজীবী রোগ",
        "symptoms": "দুর্বলতা, ওজন কমা, দুধ কম, পাতলা পায়খানা, পেট ফোলা, লোম উঠা, রক্তশূন্যতা",
        "treatment": "Albendazole বা Fenbendazole কৃমিনাশক ওষুধ, ৩ মাস পরপর দেওয়া",
        "prevention": "প্রতি ৩ মাসে কৃমিনাশক, পরিষ্কার পানি ও খাবার, খোঁয়াড় পরিষ্কার রাখা",
        "vaccine": "নেই",
        "urgency": "সাধারণ — নিয়মিত চিকিৎসায় নিয়ন্ত্রণ সম্ভব",
        "keywords": "কৃমি worm দুর্বলতা ওজন কমা পাতলা পায়খানা রক্তশূন্যতা লোম উঠা"
    },

    # ═══════════════════════════════════════
    # ছাগল — Goat Diseases
    # ═══════════════════════════════════════
    {
        "id": "goat_ppr",
        "title": "ছাগলের পিপিআর রোগ (PPR - Peste des Petits Ruminants)",
        "animal": "ছাগল ও ভেড়া",
        "category": "ভাইরাসজনিত রোগ",
        "symptoms": "উচ্চ জ্বর ১০৪-১০৬°F, চোখ-নাক দিয়ে পানি, মুখে ঘা, ডায়রিয়া, নিউমোনিয়া, মৃত্যুহার ৫০-৮০%",
        "treatment": "নির্দিষ্ট চিকিৎসা নেই, Oxytetracycline সেকেন্ডারি সংক্রমণের জন্য, Vitamin C, সহায়ক চিকিৎসা",
        "prevention": "PPR vaccine — সবচেয়ে গুরুত্বপূর্ণ, আক্রান্ত পশু আলাদা করা",
        "vaccine": "PPR Vaccine (প্রতি ৩ বছরে ১ বার, ৩ মাস বয়স থেকে)",
        "urgency": "অত্যন্ত জরুরি — মৃত্যুহার অনেক বেশি",
        "keywords": "ppr ছাগল জ্বর ডায়রিয়া মুখে ঘা নাক দিয়ে পানি মৃত্যু"
    },
    {
        "id": "goat_pneumonia",
        "title": "ছাগলের নিউমোনিয়া (Pneumonia)",
        "animal": "ছাগল",
        "category": "শ্বাসতন্ত্রের রোগ",
        "symptoms": "কাশি, শ্বাসকষ্ট, জ্বর, নাক দিয়ে সর্দি, দুর্বলতা, খাওয়া কমা",
        "treatment": "Oxytetracycline বা Tylosin injection, Antihistamine, গরম পরিবেশ রাখা",
        "prevention": "ঠান্ডা ও ভেজা পরিবেশ থেকে রক্ষা, পর্যাপ্ত পুষ্টি, ভিড় এড়ানো",
        "vaccine": "নেই",
        "urgency": "মাঝারি জরুরি",
        "keywords": "নিউমোনিয়া কাশি শ্বাসকষ্ট সর্দি জ্বর ছাগল"
    },
    {
        "id": "goat_enterotoxemia",
        "title": "ছাগলের এন্টারোটক্সেমিয়া (Enterotoxemia)",
        "animal": "ছাগল",
        "category": "ব্যাকটেরিয়াজনিত রোগ",
        "symptoms": "হঠাৎ মৃত্যু, খিঁচুনি, পেটে ব্যথা, ডায়রিয়া, মাথা পেছনে হেলানো",
        "treatment": "Antitoxin injection অবিলম্বে, Penicillin, ভেটেরিনারি সাহায্য",
        "prevention": "Enterotoxemia vaccine, হঠাৎ খাদ্য পরিবর্তন না করা, অতিরিক্ত শস্য না খাওয়ানো",
        "vaccine": "Enterotoxemia Vaccine (বছরে ২ বার)",
        "urgency": "অত্যন্ত জরুরি",
        "keywords": "এন্টারোটক্সেমিয়া হঠাৎ মৃত্যু খিঁচুনি ডায়রিয়া ছাগল"
    },

    # ═══════════════════════════════════════
    # মুরগি — Poultry Diseases
    # ═══════════════════════════════════════
    {
        "id": "hen_newcastle",
        "title": "মুরগির রানীক্ষেত রোগ (Newcastle Disease)",
        "animal": "মুরগি",
        "category": "ভাইরাসজনিত রোগ",
        "symptoms": "ঘাড় মোচড়ানো, হাঁটতে না পারা, ডিম উৎপাদন কমা, শ্বাসকষ্ট, সবুজ ডায়রিয়া, মৃত্যু",
        "treatment": "নির্দিষ্ট চিকিৎসা নেই, Antibiotic সেকেন্ডারি সংক্রমণের জন্য, Vitamin",
        "prevention": "Newcastle vaccine নিয়মিত দেওয়া সবচেয়ে গুরুত্বপূর্ণ",
        "vaccine": "Newcastle (Ranikhet) Vaccine — ৫ম দিনে eye drop, ২১তম দিনে drinking water, পরে প্রতি ২ মাসে",
        "urgency": "জরুরি — সংক্রামক",
        "keywords": "রানীক্ষেত newcastle মুরগি ঘাড় মোচড়ানো ডিম কম সবুজ পায়খানা শ্বাসকষ্ট"
    },
    {
        "id": "hen_marek",
        "title": "মুরগির মারেক রোগ (Marek's Disease)",
        "animal": "মুরগি",
        "category": "ভাইরাসজনিত রোগ",
        "symptoms": "পা ও ডানা পক্ষাঘাত, ওজন কমা, চোখের মণি ছোট হওয়া, টিউমার",
        "treatment": "চিকিৎসা নেই, আক্রান্ত মুরগি সরিয়ে ফেলুন",
        "prevention": "Marek's vaccine বাচ্চার ১ দিন বয়সে",
        "vaccine": "Marek's Vaccine (হ্যাচারিতে ১ দিন বয়সে)",
        "urgency": "মাঝারি",
        "keywords": "মারেক marek পা পক্ষাঘাত ডানা পক্ষাঘাত ওজন কমা মুরগি"
    },
    {
        "id": "hen_gumboro",
        "title": "মুরগির গামবোরো রোগ (Gumboro / IBD)",
        "animal": "মুরগি",
        "category": "ভাইরাসজনিত রোগ",
        "symptoms": "হঠাৎ অসুস্থতা, সাদা ডায়রিয়া, পালক উঠা, কাঁপুনি, ক্লোয়াকা ঠোকরানো",
        "treatment": "Electrolyte পানিতে মেশানো, Vitamin C, সহায়ক চিকিৎসা",
        "prevention": "Gumboro vaccine নিয়মিত",
        "vaccine": "Gumboro Vaccine — ১৪তম ও ২১তম দিনে",
        "urgency": "জরুরি",
        "keywords": "গামবোরো gumboro ibd সাদা ডায়রিয়া পালক উঠা কাঁপুনি মুরগি"
    },
    {
        "id": "hen_egg_drop",
        "title": "মুরগির ডিম কমে যাওয়া (Egg Drop Syndrome)",
        "animal": "মুরগি",
        "category": "ভাইরাসজনিত রোগ",
        "symptoms": "ডিম উৎপাদন হঠাৎ কমা, খোসা নরম বা ভাঙা ডিম, রঙ পরিবর্তন",
        "treatment": "নির্দিষ্ট চিকিৎসা নেই, Vitamin E ও Selenium supplement",
        "prevention": "EDS vaccine দেওয়া, সুষম খাবার",
        "vaccine": "EDS Vaccine (ডিম পাড়ার আগে)",
        "urgency": "মাঝারি",
        "keywords": "ডিম কম egg drop নরম ডিম ভাঙা ডিম মুরগি"
    },

    # ═══════════════════════════════════════
    # হাঁস — Duck Diseases
    # ═══════════════════════════════════════
    {
        "id": "duck_plague",
        "title": "হাঁসের ডাক প্লেগ (Duck Plague)",
        "animal": "হাঁস",
        "category": "ভাইরাসজনিত রোগ",
        "symptoms": "উচ্চ মৃত্যুহার, রক্তাক্ত ডায়রিয়া, চোখ দিয়ে পানি, মাথা ফোলা, পা দুর্বল",
        "treatment": "নির্দিষ্ট চিকিৎসা নেই, Antibiotic সহায়ক",
        "prevention": "Duck Plague vaccine নিয়মিত",
        "vaccine": "Duck Plague Vaccine (বছরে ২ বার)",
        "urgency": "অত্যন্ত জরুরি — মৃত্যুহার ৯০%+",
        "keywords": "ডাক প্লেগ হাঁস মৃত্যু রক্ত ডায়রিয়া মাথা ফোলা"
    },

    # ═══════════════════════════════════════
    # সাধারণ স্বাস্থ্য পরামর্শ
    # ═══════════════════════════════════════
    {
        "id": "general_vaccination_schedule",
        "title": "বাংলাদেশে গবাদি পশুর ভ্যাকসিন সিডিউল",
        "animal": "সব পশু",
        "category": "ভ্যাকসিনেশন",
        "symptoms": "প্রযোজ্য নয়",
        "treatment": "প্রযোজ্য নয়",
        "prevention": "গরু: FMD (বছরে ২ বার), HS (বছরে ২ বার), Anthrax (বছরে ১ বার), BQ (বছরে ১ বার). ছাগল: PPR (৩ বছরে ১ বার), Enterotoxemia (বছরে ২ বার). মুরগি: Newcastle (৫ দিন, ২১ দিন, প্রতি ২ মাস), Gumboro (১৪, ২১ দিন)",
        "vaccine": "সব ভ্যাকসিন সরকারি ভেটেরিনারি হাসপাতাল থেকে পাওয়া যায়",
        "urgency": "নিয়মিত",
        "keywords": "ভ্যাকসিন schedule সিডিউল টিকা fmd hs anthrax ppr newcastle gumboro"
    },
    {
        "id": "general_nutrition",
        "title": "গবাদি পশুর পুষ্টি ও খাদ্য ব্যবস্থাপনা",
        "animal": "সব পশু",
        "category": "পুষ্টি ও খাদ্য",
        "symptoms": "প্রযোজ্য নয়",
        "treatment": "প্রযোজ্য নয়",
        "prevention": "গরুর দৈনিক খাবার: সবুজ ঘাস ২০-৩০ কেজি, খড় ৩-৫ কেজি, দানাদার খাবার ২-৩ কেজি (দুধেলা গরুর জন্য বেশি). পানি: প্রতিদিন ৩০-৫০ লিটার পরিষ্কার পানি. Mineral salt lick সবসময় রাখুন. ছাগল: দানাদার ২০০-৩০০ গ্রাম, ঘাস-লতাপাতা পর্যাপ্ত. মুরগি: Layer feed ১২০ গ্রাম/দিন, Calcium supplement",
        "vaccine": "প্রযোজ্য নয়",
        "urgency": "নিয়মিত",
        "keywords": "খাবার পুষ্টি nutrition feed ঘাস দানাদার পানি mineral salt"
    },
    {
        "id": "general_milk_production",
        "title": "দুধ উৎপাদন কমে যাওয়ার কারণ ও সমাধান",
        "animal": "গরু",
        "category": "উৎপাদন সমস্যা",
        "symptoms": "দুধ কমে যাওয়া",
        "treatment": "কারণ অনুযায়ী: Mastitis হলে antibiotic, পুষ্টি কম হলে খাবার বাড়ান, stress হলে পরিবেশ উন্নত করুন, Oxytocin injection (শুধু ডাক্তারের পরামর্শে)",
        "prevention": "সুষম খাবার, নিয়মিত দোহানো, পরিষ্কার পরিবেশ, stress কমানো, নিয়মিত ভ্যাকসিন",
        "vaccine": "নির্দিষ্ট নেই",
        "urgency": "মাঝারি",
        "keywords": "দুধ কম milk production কমে গেছে উৎপাদন কম"
    },
    {
        "id": "general_financial_advice",
        "title": "খামারের আর্থিক ব্যবস্থাপনা ও ROI উন্নতি",
        "animal": "সব পশু",
        "category": "আর্থিক পরামর্শ",
        "symptoms": "প্রযোজ্য নয়",
        "treatment": "প্রযোজ্য নয়",
        "prevention": "লাভ বাড়াতে: ১) Feed conversion ratio উন্নত করুন, ২) রোগ প্রতিরোধে বিনিয়োগ করুন (চিকিৎসার চেয়ে সস্তা), ৩) উচ্চ উৎপাদনশীল জাত বেছে নিন, ৪) দুধ ও মাংস সঠিক বাজারে বেচুন, ৫) রেকর্ড রাখুন প্রতিটা পশুর আলাদাভাবে",
        "vaccine": "প্রযোজ্য নয়",
        "urgency": "সাধারণ",
        "keywords": "লাভ profit roi আর্থিক income খরচ কমানো উৎপাদন বাড়ানো বিনিয়োগ"
    },
]