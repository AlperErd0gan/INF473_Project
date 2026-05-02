GSU_BIL_REQUIREMENTS = {
    "min_gpa": 2.0,
    "min_ects": 240,
    "language_requirement": "12 credits foreign language passed OR English B2+",
    "mandatory_courses": [
        # Semester 1
        {"code": "ING106", "name": "Matematik I", "ects": 7, "semester": 1},
        {"code": "ING116", "name": "Fizik I", "ects": 5, "semester": 1},
        {"code": "ING111", "name": "Ekonominin Temelleri", "ects": 4, "semester": 1},
        {"code": "INF112", "name": "Programlamaya Giriş", "ects": 4, "semester": 1},
        {"code": "INF113", "name": "Bilgisayar Mühendisliğine Giriş", "ects": 4, "semester": 1},
        {"code": "FLF101", "name": "Fransızca CEF B2.1 Akademik", "ects": 2, "semester": 1},
        # Semester 2
        {"code": "ING107", "name": "Matematik II", "ects": 7, "semester": 2},
        {"code": "ING117", "name": "Fizik II", "ects": 5, "semester": 2},
        {"code": "INF114", "name": "İleri Bilgisayar Programlama", "ects": 5, "semester": 2},
        {"code": "INF116", "name": "Bilgisayar Sistemlerine Giriş", "ects": 5, "semester": 2},
        {"code": "CNT120", "name": "Girişimcilik ve Kariyer Planlama", "ects": 2, "semester": 2},
        {"code": "FLF201", "name": "Fransızca CEF B2.2 Akademik", "ects": 2, "semester": 2},
        # Semester 3
        {"code": "ING251", "name": "Yüksek Matematik I", "ects": 4, "semester": 3},
        {"code": "ING207", "name": "Lineer Cebir", "ects": 5, "semester": 3},
        {"code": "INF256", "name": "Olasılık", "ects": 5, "semester": 3},
        {"code": "ING229", "name": "Analog Elektronik", "ects": 7, "semester": 3},
        {"code": "INF224", "name": "Veri Yapısı ve Algoritmalar", "ects": 5, "semester": 3},
        # Semester 4
        {"code": "ING252", "name": "Yüksek Matematik II", "ects": 4, "semester": 4},
        {"code": "ING208", "name": "Diferansiyel Denklemler", "ects": 4, "semester": 4},
        {"code": "INF257", "name": "İstatistik ve Veri Analizi", "ects": 5, "semester": 4},
        {"code": "ING220", "name": "Sayısal Elektronik", "ects": 5, "semester": 4},
        {"code": "INF243", "name": "Nesneye Yönelik Programlama", "ects": 5, "semester": 4},
        {"code": "INF291", "name": "Staj I", "ects": 3, "semester": 4},
        # Semester 5
        {"code": "INF356", "name": "Veri Analizine Giriş", "ects": 4, "semester": 5},
        {"code": "INF324", "name": "Veri Tabanı Tasarımı ve Uygulamaları", "ects": 5, "semester": 5},
        {"code": "INF315", "name": "Kesikli Matematik", "ects": 4, "semester": 5},
        {"code": "INF345", "name": "Sayısal Sinyal İşleme", "ects": 5, "semester": 5},
        {"code": "CNT250", "name": "Bilgisayar Mühendisleri için Proje Risk ve Değişiklik Yönetimi", "ects": 2, "semester": 5},
        {"code": "INF320", "name": "Bilgisayar Mimarisi", "ects": 5, "semester": 5},
        # Semester 6
        {"code": "INF323", "name": "Otomatlar ve Diller Teorisi", "ects": 4, "semester": 6},
        {"code": "INF333", "name": "İşletim Sistemleri", "ects": 5, "semester": 6},
        {"code": "INF325", "name": "Sayısal Analiz", "ects": 4, "semester": 6},
        {"code": "INF340", "name": "Mikroişlemciler", "ects": 5, "semester": 6},
        {"code": "INF334", "name": "Bilgisayar Ağları", "ects": 4, "semester": 6},
        {"code": "INF399", "name": "Staj II", "ects": 2, "semester": 6},
        # Semester 7
        {"code": "INF443", "name": "Dağıtık Sistemler ve Uygulamalar", "ects": 4, "semester": 7},
        {"code": "INF402", "name": "Nesnelerin İnternetine Giriş", "ects": 3, "semester": 7},
        {"code": "INF444", "name": "Yapay Zeka", "ects": 5, "semester": 7},
        {"code": "INF493", "name": "Bilgisayar Mühendisliğinde Araştırma Konuları", "ects": 3, "semester": 7},
        {"code": "INF471", "name": "Bilişimde Güvenlik", "ects": 4, "semester": 7},
        {"code": "INF400", "name": "Veri Derlemesi", "ects": 5, "semester": 7},
        # Semester 8
        {"code": "INF481", "name": "Yazılım Mühendisliği ve Nesneye Yönelik Tasarım", "ects": 5, "semester": 8},
        {"code": "INF482", "name": "Gömülü Sistem Tasarım Temelleri", "ects": 5, "semester": 8},
        {"code": "INF494", "name": "Bitirme Projesi", "ects": 6, "semester": 8},
    ],
    "elective_groups": [
        {
            "semester": 5,
            "required_count": 1,
            "ects_each": 5,
            "options": [
                {"code": "INF353", "name": "Web Programlama"},
                {"code": "INF354", "name": "Bilişimde Oyun Teorisi ve Uygulamaları"},
                {"code": "INF454", "name": "İnsan Bilgisayar Etkileşiminin Temelleri"},
            ],
        },
        {
            "semester": 6,
            "required_count": 2,
            "ects_each": 5,
            "options": [
                {"code": "INF330", "name": "Robotik"},
                {"code": "INF360", "name": "Veri Tabanı Yönetimi ve Güvenliği"},
                {"code": "INF365", "name": "Haberleşme ve Multimedya"},
                {"code": "INF366", "name": "Sayısal Görüntü İşleme"},
            ],
        },
        {
            "semester": 7,
            "required_count": 1,
            "ects_each": 5,
            "options": [
                {"code": "INF438", "name": "İleri Veri Tabanları"},
                {"code": "INF410", "name": "Medical Informatics"},
                {"code": "INF432", "name": "Bilgisayar Grafikleri"},
                {"code": "INF430", "name": "Robotik"},
            ],
        },
        {
            "semester": 8,
            "required_count": 2,
            "ects_each": 5,
            "options": [
                {"code": "INF472", "name": "Bulut Bilişim"},
                {"code": "INF473", "name": "Üretken Yapay Zekaya Giriş"},
                {"code": "INF474", "name": "Wireless and Mobile Networks"},
                {"code": "INF475", "name": "Kullanıcı Arayüzü ve Deneyimi Tasarımı"},
                {"code": "INF483", "name": "Bilgi Çıkarımı ve Veri Madenciliğine Giriş"},
                {"code": "INF437", "name": "Sistem Mühendisliği"},
                {"code": "INF441", "name": "Şifrelemeye Giriş"},
                {"code": "INF446", "name": "Bilgisayar Mühendisliğinde Özel Konular"},
            ],
        },
        {
            "semester": 8,
            "required_count": 1,
            "ects_each": 4,
            "description": "IND seçmeli",
            "options": [
                {"code": "IND471", "name": "Yöneylem Araştırması"},
                {"code": "IND472", "name": "Mühendislik Ekonomisi"},
                {"code": "MAT383", "name": "Matematiksel Modelleme ve Simülasyona Giriş"},
            ],
        },
        {
            "semester": 8,
            "required_count": 1,
            "ects_each": None,
            "description": "CNT or CC elective",
            "options": [
                {"code": "CNT416", "name": "Sosyal Medya", "ects": 2},
                {"code": "CNT414", "name": "Felsefe", "ects": 2},
                {"code": "CNT417", "name": "Girişimcilik", "ects": 2},
                {"code": "CNT412", "name": "Bilişim Hukuku", "ects": 2},
                {"code": "CNT411", "name": "Fotoğrafçılık", "ects": 2},
                {"code": "MAT393", "name": "Matematik ve Toplum", "ects": 3},
                {"code": "CC301", "name": "Psikolojiye Giriş", "ects": 3},
                {"code": "CC303", "name": "Finansal Okuryazarlık", "ects": 3},
                {"code": "CC304", "name": "Denizcilik Tarihi ve Kültürü", "ects": 3},
                {"code": "CC305", "name": "Etnomüzikoloji", "ects": 3},
                {"code": "CC307", "name": "İstanbul'un Kültürel Mirası", "ects": 3},
                {"code": "CC309", "name": "Mitoloji ve İkonografi", "ects": 3},
                {"code": "CC311", "name": "Yapay Zekâ Çağında Problem Çözüm Teknikleri", "ects": 3},
                {"code": "CC302", "name": "Disiplinlerarası Yapay Zeka ve Uygulamaları", "ects": 3},
                {"code": "CC306", "name": "Medeniyetler Tarihi", "ects": 3},
                {"code": "CC308", "name": "Klasik Türk Müziği’ne Giriş", "ects": 3},
                {"code": "CC310", "name": "Çağlar Boyunca Türk Sanatı", "ects": 3},
                {"code": "CC312", "name": "İstanbul Tarihi ve Kültürel Mirası", "ects": 3},
                {"code": "CC314", "name": "Kültür Mirası", "ects": 3},
            ],
        },
    ],
    "course_equivalencies": {
        # Program değişikliği notlarına göre (2024-2025 ve öncesi)
        "ING111": ["ING127", "ING125"],  # Kimya derslerinden geçiş
        "ING106": ["ING104"],  # Matematik I eski kodu
        "ING116": ["ING114"],  # Fizik I eski kodu
        "ING107": ["ING105"],  # Matematik II eski kodu
        "ING117": ["ING115"],  # Fizik II eski kodu
        "INF345": ["INF316"],  # Sinyaller ve Sistemler -> Sayısal Sinyal İşleme
        "CNT250": ["CNT350"],  # Proje/Risk dersi kod değişimi
        "INF330": ["INF430"],  # Robotik kod değişimi (7. yarıyıl notu)
        "INF402": ["INF470"],  # Ağ labı -> IoT dönüşümü
        "INF256": ["INF204"],  # Eski elektromanyetik dalgalar dersi
        "INF257": ["INF211"],  # Eski olasılık-istatistik dersi
        "ING251": ["ING203"],  # Yüksek matematik I kod değişimi
        "ING252": ["ING204"],  # Yüksek matematik II kod değişimi
        "INF243": ["INF223"],  # OOP kod değişimi
        "INF291": ["INF299"],  # Staj kod değişimi
        "FLF101": ["TUR001"],  # Eski plan 1. dönem ortak ders karşılığı
        "FLF201": ["TUR002"],  # Eski plan 2. dönem ortak ders karşılığı
        # Eski öğretim planı seçmeli kodları
        "INF454": ["INF352"],  # İnsan Bilgisayar Etkileşimi kod değişimi
        # 2020-2021 ve öncesi kod karşılıkları
        "INF112": ["INF102"],
        "INF113": ["INF101"],
        "INF114": ["INF103"],
    },
    "notes": [
        "If total ECTS < 240, student must take additional INF electives to fill the gap.",
    ],
}
