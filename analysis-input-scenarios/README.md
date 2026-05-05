# Özel Senaryo Transkriptleri (Eski Müfredat / Eşdeğerlik)

Bu klasördeki her `.txt` dosyası **tekil bir transkripttir** ve doğrudan yüklenebilir.

## Senaryolar

1. `01-legacy-baseline-pass.txt`
   - Amaç: Eski müfredat için baz/pozitif kontrol.
   - Beklenti: Zorunlu ders ve gereksinim kontrolleri geçer.

2. `02-legacy-failed-inf112-extra-social.txt`
   - Amaç: `INF112` başarısızlığı sonrası ilave sosyal seçmeli kuralını tetiklemek.
   - Beklenti: `Geçiş kuralları nedeniyle ilave sosyal seçmeli` uyarısı.

3. `03-legacy-failed-inf470-extra-inf.txt`
   - Amaç: `INF402` geçmiş olsa bile `INF470` başarısızlığının ilave INF seçmeli etkisini test etmek.
   - Beklenti: `Geçiş kuralları nedeniyle ilave INF seçmeli` uyarısı.

4. `04-legacy-failed-ing144-needs-inf321.txt`
   - Amaç: `ING144` başarısızlığı için `INF321` telafi kuralını test etmek.
   - Beklenti: `INF321 Teknik Resim dersi tamamlanmalı` uyarısı.

5. `05-modern-one-sem6-elective.txt`
   - Amaç: 2024-2025 planında 6. dönemde tek INF seçmeli ile kuralın sağlandığını test etmek.
   - Beklenti: 6. dönem INF seçmeli eksiği oluşmaz (senaryo geçer).

6. `06-equivalency-old-codes-mixed.txt`
   - Amaç: Eski/yeni kod eşdeğerliklerini (ING104->ING106, INF470->INF402 vb.) birlikte test etmek.
   - Beklenti: Zorunlu ders eşleşmelerinin eşdeğer kodlarla tamam sayılması.

7. `07-low-gpa-fail.txt`
   - Amaç: Sadece GNO eşiği altında kalma durumunu test etmek.
   - Beklenti: `GNO yetersiz` nedeniyle mezun olamaz.

8. `08-language-requirement-fail.txt`
   - Amaç: Dil koşulu sağlanmadığında analiz çıktısını test etmek.
   - Beklenti: `Dil koşulu sağlanmadı` uyarısı.

9. `09-ects-below-240.txt`
   - Amaç: 240 AKTS altı durumda AKTS doğrulamasını test etmek.
   - Beklenti: `AKTS yetersiz` uyarısı.

10. `10-missing-mandatory-inf482.txt`
    - Amaç: Tek bir zorunlu ders eksiği durumunu test etmek.
    - Beklenti: `INF482` eksik zorunlu ders olarak listelenir.

11. `11-legacy-failed-inf115-compensated-pass.txt`
    - Amaç: `INF115` başarısızlığı olsa da ilave INF seçmeli açığının telafi edildiği durumu test etmek.
    - Beklenti: Senaryo geçer.

12. `12-legacy-multi-extra-inf-fail.txt`
    - Amaç: Birden fazla geçiş kuralı nedeniyle ilave INF seçmeli açığının oluştuğu durumu test etmek.
    - Beklenti: İlave INF seçmeli eksikliği nedeniyle mezun olamaz.

13. `13-inf112-failed-but-recovered-pass.txt`
    - Amaç: `INF112` başarısızlığı sonrası dersi tekrar geçip ilave sosyal seçmeliyi tamamlanan durumu test etmek.
    - Beklenti: Senaryo geçer.

14. `14-modern-sem6-two-elective-pass.txt`
    - Amaç: Modern planda 6. dönem INF seçmeli (2 adet) koşulunun sağlandığı durumu test etmek.
    - Beklenti: Senaryo geçer.

15. `15-modern-sem6-one-elective-fail.txt`
    - Amaç: Modern planda 6. dönem INF seçmeli koşulunun eksik kaldığı durumu test etmek.
    - Beklenti: `Dönem 6 INF seçmeli` eksikliği nedeniyle mezun olamaz.

16. `16-2020-code-equivalency-pass.txt`
    - Amaç: `INF102/INF101/INF103` gibi 2020 kodlarının eşdeğerlikten sayılmasını test etmek.
    - Beklenti: Eşdeğerlikler doğru sayılır ve senaryo geçer.

17. `17-modern-missing-semester5-inf-elective.txt`
    - Amaç: Modern planda 5. dönem INF seçmeli grubunun eksik kalmasını test etmek.
    - Beklenti: `Dönem 5 INF seçmeli` eksikliği nedeniyle mezun olamaz.

18. `18-modern-missing-semester7-inf-elective.txt`
    - Amaç: Modern planda 7. dönem INF seçmeli grubunun eksik kalmasını test etmek.
    - Beklenti: `Dönem 7 INF seçmeli` eksikliği nedeniyle mezun olamaz.

19. `19-modern-missing-ind-elective.txt`
    - Amaç: Modern planda 8. dönem IND seçmeli koşulunun eksik kalmasını test etmek.
    - Beklenti: `Dönem 8 IND seçmeli` eksikliği nedeniyle mezun olamaz.

20. `20-modern-missing-social-elective.txt`
    - Amaç: Modern planda CNT/CC sosyal seçmeli koşulunun eksik kalmasını test etmek.
    - Beklenti: `Dönem 8 CNT or CC elective` eksikliği nedeniyle mezun olamaz.
