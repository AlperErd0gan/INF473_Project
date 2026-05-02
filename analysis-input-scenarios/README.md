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
   - Amaç: Modern plan (legacy marker yok) için 6. dönem INF seçmeli sayımını test etmek.
   - Beklenti: `Dönem 6 INF seçmeli: 1 ders eksik`.

6. `06-equivalency-old-codes-mixed.txt`
   - Amaç: Eski/yeni kod eşdeğerliklerini (ING104->ING106, INF470->INF402 vb.) birlikte test etmek.
   - Beklenti: Zorunlu ders eşleşmelerinin eşdeğer kodlarla tamam sayılması.
