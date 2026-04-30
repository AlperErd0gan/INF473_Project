import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
from agent import run_analysis_pipeline
import json

transcript = """ÖĞRENCİ: Zeynep Arslan | 2020401007
GPA: 3.42

ING106 Matematik I - AA - 7 AKTS
ING116 Fizik I - AA - 5 AKTS
ING111 Ekonominin Temelleri - BB - 4 AKTS
INF112 Programlamaya Giriş - AA - 4 AKTS
INF113 Bilgisayar Mühendisliğine Giriş - AA - 4 AKTS
FLF101 Fransızca B2.1 - BB - 2 AKTS
ING107 Matematik II - AA - 7 AKTS
ING117 Fizik II - BB - 5 AKTS
INF114 İleri Bilgisayar Programlama - AA - 5 AKTS
INF116 Bilgisayar Sistemlerine Giriş - AA - 5 AKTS
CNT120 Girişimcilik ve Kariyer Planlama - AA - 2 AKTS
FLF201 Fransızca B2.2 - BB - 2 AKTS
ING251 Yüksek Matematik I - BB - 4 AKTS
ING207 Lineer Cebir - AA - 5 AKTS
INF256 Olasılık - AA - 5 AKTS
ING229 Analog Elektronik - BB - 7 AKTS
INF224 Veri Yapısı ve Algoritmalar - AA - 5 AKTS
ING252 Yüksek Matematik II - BB - 4 AKTS
ING208 Diferansiyel Denklemler - BB - 4 AKTS
INF257 İstatistik ve Veri Analizi - AA - 5 AKTS
ING220 Sayısal Elektronik - BB - 5 AKTS
INF243 Nesneye Yönelik Programlama - AA - 5 AKTS
INF291 Staj I - Başarılı - 3 AKTS
INF356 Veri Analizine Giriş - AA - 4 AKTS
INF324 Veri Tabanı Tasarımı ve Uygulamaları - AA - 5 AKTS
INF315 Kesikli Matematik - BB - 4 AKTS
INF345 Sayısal Sinyal İşleme - BB - 5 AKTS
CNT250 Proje Risk ve Değişiklik Yönetimi - AA - 2 AKTS
INF320 Bilgisayar Mimarisi - BB - 5 AKTS
INF353 Web Programlama - AA - 5 AKTS
INF323 Otomatlar ve Diller Teorisi - BB - 4 AKTS
INF333 İşletim Sistemleri - AA - 5 AKTS
INF325 Sayısal Analiz - BB - 4 AKTS
INF340 Mikroişlemciler - BB - 5 AKTS
INF334 Bilgisayar Ağları - AA - 4 AKTS
INF399 Staj II - Başarılı - 2 AKTS
INF330 Robotik - BB - 5 AKTS
INF360 Veri Tabanı Yönetimi ve Güvenliği - AA - 5 AKTS
INF443 Dağıtık Sistemler ve Uygulamalar - BB - 4 AKTS
INF402 Nesnelerin İnternetine Giriş - BB - 3 AKTS
INF444 Yapay Zeka - AA - 5 AKTS
INF493 Araştırma Konuları - BB - 3 AKTS
INF471 Bilişimde Güvenlik - AA - 4 AKTS
INF400 Veri Derlemesi - BB - 5 AKTS
INF438 İleri Veri Tabanları - AA - 5 AKTS
INF481 Yazılım Mühendisliği ve Nesneye Yönelik Tasarım - AA - 5 AKTS
INF482 Gömülü Sistem Tasarım Temelleri - BB - 5 AKTS
INF494 Bitirme Projesi - AA - 6 AKTS
INF472 Bulut Bilişim - AA - 5 AKTS
INF473 Üretken Yapay Zekaya Giriş - BB - 5 AKTS
IND471 Yöneylem Araştırması - BB - 4 AKTS
CC307 İstanbul'un Kültürel Mirası - AA - 3 AKTS"""

result = run_analysis_pipeline(transcript)
print(json.dumps({
    "Toplam ECTS": result["transcript_total_ects"],
    "Gerekli ECTS": result["required_ects"],
    "GNO": result["gpa"],
    "Mezun Mu": result["is_graduated"],
    "Eksik Koşullar": result["missing_conditions"],
    "Rapor": result["report_text"]
}, indent=2, ensure_ascii=False))
