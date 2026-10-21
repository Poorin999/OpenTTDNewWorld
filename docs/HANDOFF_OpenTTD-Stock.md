# OpenTTD-Stock: สรุปงานทั้งหมด สำหรับส่งต่อ AI ตัวถัดไป

ผู้ใช้พูดไทยและไม่ใช่โปรแกรมเมอร์ ต้องตอบเป็นภาษาไทย และส่งไฟล์ที่ copy-paste ลง repo ได้เลย
งานถัดไปที่ผู้ใช้ต้องการ: **แทนที่ปฏิทินของ OpenTTD ด้วยนาฬิกาใหม่** ผ่าน 3 ขั้น (ดูหัวข้อ 6)

## 1. โครงการและการบิลด์
- เป้าหมาย: แปลง OpenTTD 15.3 เป็นเกมจำลองการเทรดหุ้น (หุ้นของบริษัทผู้เล่น/AI, เทอร์มินัลแบบ MT5, ธนาคารกลาง, กระเป๋าเงินหลายใบ)
- Repo: `Poorin999/OpenTTD-Stock` (public) บิลด์ด้วย GitHub Actions บน `windows-2022` (MSVC + Ninja + vcpkg x64-windows-static)
- ขั้นตอนบิลด์: `git apply mod/stock-market.patch` แล้วคัดลอกไฟล์ม็อดลง `openttd/src/` (สคริปต์ `apply_overlay.py` / `apply_overlay.sh`) สคริปต์เพิ่มคำสั่งลง `command_type.h`, เพิ่มไฟล์ลง `src/CMakeLists.txt`, เพิ่มข้อความลง `lang/english.txt` และแก้ `economy.cpp` (รันซ้ำได้)
- ผู้ใช้ยืนยันบิลด์ผ่านถึงรอบที่ 8 รอบที่ 9 (ธนาคาร, แถบเลื่อน Market Watch) อยู่ใน repo แล้วแต่ **ยังไม่ทราบผลบิลด์** รอบที่ 10 (นาฬิกา `game_time/`) **ยังไม่ได้อัปโหลดเข้า repo** ทั้งหมดนี้ทดสอบได้แค่ `g++ -fsyntax-only` บน Linux ยังไม่เคยผ่าน MSVC
- ผู้ใช้ส่ง log บิลด์ที่ล้มเป็นภาพ ให้ขอบรรทัด `FAILED:` และ `error C` ถ้าบิลด์ล้ม

## 1.1 สถานะ repo จริง (ตรวจจาก zip `OpenTTD-Stock-main.zip` ที่ผู้ใช้ส่งมา)
โครงสร้างที่เห็น: `.github/workflows/build-windows.yml`, `apply_overlay.py`, `apply_overlay.sh`, `stock-market.patch` และโฟลเดอร์ `src/`
ผมลองประกอบ repo นี้บน OpenTTD 15.3 ต้นฉบับแบบเดียวกับ workflow (patch → คัดลอก `src/` → overlay) แล้วคอมไพล์ด้วย GCC ผ่านทุกไฟล์ (ไม่นับข้อความ `STR_` ที่เครื่องทดสอบไม่ได้สร้างไฟล์ภาษา) และทดสอบแล้วว่าชุดนาฬิกา (รอบ 10) ลงทับได้โดยไม่ขัดกับ patch

ขั้นตอนของ workflow: checkout repo นี้ไว้ที่ `mod/` และ OpenTTD 15.3 ที่ `openttd/` → `git apply mod/stock-market.patch` → คัดลอก `mod/src/*` ลง `openttd/src/` (**ล้มถ้าไฟล์ซ้ำกับของ OpenTTD**) → `python3 mod/apply_overlay.py openttd` → vcpkg → Build

`stock-market.patch` แก้ 13 ไฟล์ของ OpenTTD: `CMakeLists.txt`, `command.cpp`, `command_type.h`, `economy.cpp`, `lang/english.txt`, `network/network_command.cpp`, `saveload/CMakeLists.txt`, `saveload/compat/CMakeLists.txt`, `saveload/saveload.cpp`, `statusbar_gui.cpp`, `widgets/CMakeLists.txt`, `widgets/statusbar_widget.h`, `window_type.h` ใน `economy.cpp` patch เพิ่มแค่ `#include "stock_base.h"` และเรียก `_stock_market.Reset()` ใน `InitializeEconomy()` (จุดนี้คือที่ที่นาฬิกาเกมถูกรีเซ็ตตอนเริ่มเกมใหม่)

**ปัญหาโครงสร้างไฟล์ใน repo (ยังไม่ได้แก้ ไม่กระทบบิลด์ตอนนี้):**
- มีไฟล์ซ้ำ 2 ชุด: `src/stock_sl.cpp` และ `src/stock_widget.h` (วางผิดที่ แต่เป็น **ตัวใหม่ล่าสุด**) กับ `src/saveload/stock_sl.cpp` และ `src/widgets/stock_widget.h` (ตัวถูกที่แต่เป็น **ตัวเก่า**)
- บิลด์ยังผ่านเพราะ `apply_overlay.py` เลือกไฟล์ที่เส้นทางสั้นที่สุดก่อน จึงได้ตัวใหม่ใน `src/` ไปคัดลอกทับของเก่าใน `openttd/src/saveload/` และ `openttd/src/widgets/` แต่เป็นความเสี่ยง
- ที่ควรทำ: ลบไฟล์เก่าในโฟลเดอร์ย่อย แล้วเอาไฟล์ใหม่ใส่ในโฟลเดอร์ย่อยที่ถูกต้อง (`src/saveload/`, `src/widgets/`) และลบสำเนาที่วางผิดที่ใน `src/`
- ไฟล์ `english_stock_strings.txt`, `english_wallet_strings.txt`, `english_round8_strings.txt` อยู่ใน `src/` (ถูกคัดลอกเข้า OpenTTD ด้วยแต่ไม่เป็นไร) ควรย้ายไปที่ root ข้าง `apply_overlay.py`
- ไฟล์ `src/saveload/compat/stock_sl_compat.h` มีอยู่ และไม่ต้องแก้ ตราบที่ไม่เปลี่ยนโครง `StockRecord`

**ตรวจแล้วว่าไม่ขัดกันเอง:** แก้ `economy.cpp` ของ patch กับของ `apply_overlay.py` คนละบรรทัด; รีเซ็ตนาฬิกาผ่าน `_stock_market.Reset()` ของ patch; `SRK_TIME` ไม่ชนชนิด record เดิม; ตัวเดินนาฬิกากับตัวจับเวลาหุ้นเป็นคนละ `IntervalTimer`
**ต้องรู้:** ตอนนี้มี 2 นาฬิกาเดินพร้อมกัน ระบบหุ้นและดอกเบี้ยธนาคารกลางยังนับวันปฏิทินเดิม (1 วัน ≈ 2 วินาทีจริง) ส่วน `GameTimeManager` นับ 1 วัน = 24 นาทีจริง ยังไม่มีระบบไหนใช้นาฬิกาใหม่ จนกว่าจะทำงานขั้นที่ 1 ในหัวข้อ 6

## 2. กฎของโค้ด (ฝ่าฝืนแล้วบิลด์พังหรือเกมออนไลน์ desync)
- สถานะเกมเปลี่ยนผ่านคำสั่ง (`DEF_CMD_TRAIT`, `Command<CMD_X>::Post`) เท่านั้น ข่าวและ GUI เป็นฝั่งไคลเอนต์ล้วน
- คำนวณด้วยจำนวนเต็มเท่านั้นในส่วนที่เป็นสถานะเกม ห้ามใช้เวลาจริงของเครื่อง
- MSVC: คำสั่งที่ไม่มีพารามิเตอร์นอกจาก `flags` จะทำให้คอมไพเลอร์ล่ม (ICE C1001 ที่ `command_func.h`) ทุกคำสั่งต้องมีอาร์กิวเมนต์อย่างน้อย 1 ตัว
- `safeguards.h` ห้ามใช้ `std::to_string` ให้ใช้ `fmt::format`
- ข้อความใหม่ในเกมต้องเพิ่ม `STR_...` ลง `english.txt` (ผ่าน `english_*_strings.txt` และ `apply_overlay.py`) หรือวาดด้วย `std::string` ตรงๆ
- โค้ดเซฟอยู่ใน chunk `STCK` แบบ record เดียว (`StockRecord`: kind, a, b, ym, v1..v5) เพิ่มชนิด record ใหม่ได้โดยไม่ต้องเปลี่ยนเวอร์ชันเซฟ ชนิดที่มี: `SRK_CANDLE 0, RUNNING 1, PRICE 2, POSITION 4, PENDING 5, META 6, VALUATION 7, HISTORY 8, MARKET 9, BALANCE 10, DAILY 11, DAILY_RUNNING 12, DAILY_ON 13, WALLET 14, POSITION_EXT 15, STATS 16, STATS_MONTH 17, BANK 18, TIME 19`

## 3. ไฟล์ม็อด (ทั้งหมดอยู่ใน `src/` ยกเว้นที่ระบุ)
| หมวด | ไฟล์ | หน้าที่ |
|---|---|---|
| หุ้น: ข้อมูล | `stock_base.h/.cpp` | ราคา (มูลค่าบริษัท/100,000 หุ้น), แท่งเทียนรายวัน/เดือน, ตำแหน่ง/ออเดอร์รอ, margin call/stop-out, swap, เงินปันผล, trailing stop, สถิติพอร์ต, อันดับบริษัท, ราคาขยับตามแรงซื้อขาย |
| หุ้น: คำสั่ง | `stock_cmd.h/.cpp` | `CmdStockOpen/Close/Modify(+trail)/Transfer/EnableDaily` |
| หุ้น: หน้าจอ | `stock_gui.h/.cpp`, `stock_order_gui.cpp`, `widgets/stock_widget.h` | Market Watch (มีแถบเลื่อน), กราฟ (SMA10/30, Volume, RSI), Toolbox, มุมมอง Orders/History/Portfolio/Ranking/Bank, ปุ่ม Close All |
| กระเป๋าเงิน | `wallet_base.h/.cpp`, `wallet_cmd.h/.cpp` | เงินสดหลัก(0), กระเป๋าเทรด 1-5, กระเป๋าเชื้อเพลิง 1; `CmdWalletCreate/Delete/Transfer` |
| ธนาคารกลาง | `central_bank.h/.cpp` | กู้/คืนเงินเข้ากระเป๋า `CmdBankBorrow/Repay`, ดอกเบี้ย 274 ppm ต่อวัน (ประมาณ 10% ต่อปี) ทบเข้าหนี้ วงเงิน 50% ของส่วนทุนสุทธิ |
| นาฬิกาเกม | `game_time/game_time_manager.h/.cpp`, `game_time/game_time_driver.cpp` | `GameTimeManager` (ดูหัวข้อ 4) |
| เซฟ | `saveload/stock_sl.cpp` | เซฟ/โหลดทุกอย่างข้างบน |
| ตัวช่วยลง | `apply_overlay.py`, `english_stock_strings.txt`, `english_wallet_strings.txt`, `english_round8_strings.txt` | |

ไฟล์เดิมของ OpenTTD ที่ม็อดแก้: `command_type.h`, `CMakeLists.txt`, `lang/english.txt`, `economy.cpp` และไฟล์อื่นที่ `stock-market.patch` แก้ (ยังไม่ได้ตรวจครบ)

## 4. นาฬิกาเกม (รอบที่ 10)
- 1 นาทีเกม = 1 วินาทีจริง, 1 ชั่วโมง = 60 นาที, 1 วัน = 24 ชั่วโมง = 1,440 นาที (24 นาทีจริง), 1 ปี = 365 วัน (ไม่มีปีอธิกสุรทิน) ปีเริ่มต้น 1950
- เดินด้วย **tick ของเกม** (`MILLISECONDS_PER_TICK` = 27 ms ต่อ tick, จำนวนเต็ม) ไม่ใช่เวลาจริง เพื่อให้ทุกเครื่องในเกมออนไลน์ตรงกัน ทำให้หยุดเกมแล้วเวลาหยุด เร่งเกมแล้วเวลาเร็วขึ้น ที่ความเร็วปกติ 1 นาทีเกม = ประมาณ 37 tick
- API: `GetCurrentGameMinute/Hour/Day/Year`, `GetTotalGameMinutes`, `GetSnapshot`, `AdvanceMilliseconds`, `Reset`, `Restore`, `Subscribe/Unsubscribe`, `OnMinuteUpdate/OnHourlyUpdate/OnDailyUpdate` และ RAII `GameTimeSubscription(GameTimeEvent::Day, [](const GameTimeSnapshot&){...}, priority)`
- ปลอดภัยหลายเธรด (mutex + atomic), เรียก callback นอก lock, รองรับ callback ที่สมัคร/ยกเลิก/เรียก Advance ซ้อน, ยิงเหตุการณ์ครบทุกนาทีเมื่อข้ามเวลาเป็นก้อน ผ่านการทดสอบแยกแล้ว
- สวิตช์ชั่วคราวที่ต้นไฟล์ `game_time_manager.h`: `GAME_TIME_DECOUPLE_CHART = true` (ไม่วาดกราฟ ข้อมูลแท่งเทียนยังบันทึก) และ `GAME_TIME_BYPASS_LEGACY_LOANS = true` (ไม่คิดดอกเบี้ยรายเดือนของเงินกู้เดิมใน `economy.cpp`)
- **ยังไม่มีระบบไหนย้ายมาสมัครรับเหตุการณ์ของนาฬิกาใหม่** และปฏิทินเดิมของ OpenTTD ยังทำงานตามปกติ

## 5. ระบบที่ผูกกับวัน/เดือน/ปีเดิม (ต้องย้ายหรือปรับ)
- `stock_base.cpp`: `_stock_daily` (`TimerGameEconomy::DAY`) อัปเดตราคา, แท่งเทียน, swap, หมดอายุออเดอร์, เงินปันผล; `_stock_tick` ทุก 8 tick (`STOCK_TICK_INTERVAL`) ปรับราคาและตรวจ SL/TP/margin; เงินปันผลอ่านผลประกอบการรายไตรมาสจาก `Company::old_economy` ของเกมเดิม
- `stock_base.cpp`: `GetStockCurrentMonth()` และแท่งเทียนรายเดือน/วัน ใช้ `TimerGameEconomy::year/month/date`
- `central_bank.cpp`: `_bank_daily` ใช้ `TimerGameEconomy::DAY` (ดอกเบี้ยต่อวัน 274 ppm)
- `stock_gui.cpp`: ป้ายวันที่ของกราฟใช้ `TimerGameEconomy::ConvertDateToYMD`
- ค่าคงที่ที่ผูกกับความยาวของวันและต้องปรับ: `STOCK_SWAP_PPM_PER_DAY`, `STOCK_IMPACT_DECAY_DIV`, `STOCK_GLIDE_DIV`, `STOCK_TICK_INTERVAL`, `STOCK_DIVIDEND_DELAY_DAYS`, `STOCK_MAX_EXPIRY_DAYS`, `CENTRAL_BANK_RATE_PPM_PER_DAY`

## 6. งานถัดไป: แทนที่ปฏิทิน (ผู้ใช้เลือกข้อ 1, 2, 3)
ข้อเท็จจริงจากซอร์ส: ความยาววันกำหนดที่ `timer/timer_game_tick.h` (`DAY_TICKS = 74`, ประมาณ 2 วินาทีจริง) ค่านี้ถูกใช้ตรงๆ 26 ไฟล์ ระบบเวลาแบ่งเป็นปฏิทิน (`TimerGameCalendar` 115 ไฟล์) และเศรษฐกิจ (`TimerGameEconomy` 70 ไฟล์) การให้วันยาว 24 นาที (ประมาณ 53,000 tick หรือมากกว่าเดิม 700 เท่า) ทำให้ค่าใช้จ่ายของรถที่คิดรายวัน (`OnNewEconomyDay`) ลดลงเหลือ 1/700 ของรายได้จากส่งสินค้า เศรษฐกิจจะเพี้ยน

ลำดับที่ตกลงกัน:
1. **ย้ายระบบม็อดทั้งหมดมาสมัครรับเหตุการณ์ของ `GameTimeManager`** (หุ้นรายวัน, ธนาคารกลาง, เงินปันผล, swap, หมดอายุออเดอร์) ปรับค่าคงที่ในหัวข้อ 5 ให้ตรงกับวันที่ยาว 24 นาที และเลิกใช้ `TimerGameEconomy` ในไฟล์ม็อด เซฟเก็บ "นาทีรวม" แทนวันที่เดิม
2. **ปรับสมดุลเศรษฐกิจบนนาฬิกาใหม่**: ค่าใช้จ่ายรถ, รายได้, การเติบโตเมือง/อุตสาหกรรม, ผลประกอบการรายไตรมาสที่ใช้คำนวณราคาหุ้นและเงินปันผล
3. **เปลี่ยน `DAY_TICKS` และแก้ 26 ไฟล์ที่ใช้ค่านี้โดยตรง** พร้อมทดสอบเซฟเก่าและเกมออนไลน์ แนะนำให้เริ่มเกมใหม่เพราะเซฟเก่าวันที่จะเพี้ยน

กฎ: ทำทีละขั้น คอมไพล์และทดสอบก่อนส่ง ห้ามแก้ระบบที่ทำงานอยู่แล้วโดยไม่จำเป็น

## 7. ที่ยังไม่ได้ทำ (แผนเดิมของผู้ใช้)
- เพดานทองคำ (Gold Standard/`gold_reserve`) คุมปริมาณเงิน, เงินสำรองตามกฎหมายและตารางภาษี (มีในไฟล์เก่าของรอบ 7 ที่ยังไม่ได้ย้ายมา)
- Finance AI Player (สคริปต์ AI), Central Bank AI (ปรับดอกเบี้ยอัตโนมัติ, พันธบัตรรัฐบาลเป็น cash sink)
- ระบบเชื้อเพลิง (จ่ายจากกระเป๋าเชื้อเพลิง; กระเป๋ามีแล้วแต่ยังไม่มีอะไรเรียกใช้), สัญญาต่อรองซื้อขายสินค้า, ค่าเช่ารางร่วม, หน้าต่างข่าว/วิเคราะห์ RSI/MA
- เมืองธนาคารกลาง, การเติบโตของเมืองผูกกับเงินกู้, ราคาหุ้นกระทบคะแนนเมือง, ฟิวเจอร์ส, การเทรดทรัพยากร
- ผู้ใช้เคยขอให้จัดไฟล์แยกโฟลเดอร์ตามหมวด (ตอนนี้มีแต่ `game_time/` ที่แยก)
