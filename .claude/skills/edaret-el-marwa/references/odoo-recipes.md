# وصفة الوصول لأودو — Odoo JSON-RPC recipes & gotchas

## العميل
الملف `odoo_client.py` (في مجلد العمل/السكراتش). يقرأ البيانات من `.odoo_env.json`
(`ODOO_URL, ODOO_DB, ODOO_USER, ODOO_KEY`) ويتصل عبر curl + HTTPS proxy.

```python
from odoo_client import model, login
uid = login()                       # لازم تنادي login() للحصول على uid
rows = model(uid, "res.company", "read", [1], ["name", "currency_id"])
```

- `model(uid, "<model>", "<method>", *args, **kw)` → execute_kw.
- شغّلها بـ `python3 script.py` من مجلد السكراتش. **لا تستخدم `python3 -I`** — يكسر
  استيراد `odoo_client`. والـ cwd بيترجع بعد كل أمر، فثبّت المسارات المطلقة.

## أنماط الاستعلام الصحيحة
- **domain = قائمة مسطّحة من leaves**، كل leaf tuple من 3 عناصر:
  ```python
  model(uid, "stock.move", "search_read", [["picking_type_id","=",351]], fields=["id"], limit=1)
  model(uid, "stock.move", "search_count", [["picking_type_id","=",351]])
  ```
- **empty domain = `[]`** وليس `[[]]`. الخطأ الشائع `IndexError: tuple index out of range`
  سببه تمرير `[[]]` — استخدم `[]`.
- **IDs تُمرّر مباشرة** (غير ملفوفة): `model(uid,"account.move.line","reconcile",[id1,id2])`.
  اللف المزدوج `[[...]]` يسبّب `unhashable type: list`.
- استخدم `fields=[...]` كـ kwarg مع `search_read`.
- أوبريتورات منطقية في الـ domain: `"|"`, `"&"`, `"!"` كعناصر منفصلة قبل الـ leaves.

## عمليات شائعة
```python
# مطابقة / فكّ مطابقة
model(uid,"account.move.line","reconcile",[id1,id2])
model(uid,"account.move.line","remove_move_reconcile",[id1,id2])   # ids مباشرة
# حذف قيد مرحّل: سوّده ثم احذفه
model(uid,"account.move","button_draft",[move_id]); model(uid,"account.move","unlink",[move_id])
# POS
sess = model(uid,"pos.session","search",[["config_id","=",97]])
model(uid,"pos.session","read",sess,["name","cash_register_balance_end_real","cash_register_difference","state"])
model(uid,"pos.order.line","search_read",[["order_id","in",orders],["discount",">",25]],fields=["discount","product_id","qty"])
# مخزون
model(uid,"stock.quant","search_count",[["quantity","<",0],["location_id.usage","=","internal"]])
model(uid,"stock.valuation.layer","search_read",[["create_date",">=","2026-01-01"]],fields=["value","quantity"])
```

## تحذيرات بيانات
- **المخزن مشترك** (Main Store) عبر الفروع → تسويات الجرد/العجز على مستوى الشركة،
  **لا تنسبها لفرع واحد**. (مجموع تسويات 2026 يطلع ملايين لأنه الشركة كلها.)
- البيع بدون فاتورة **لا يترك أثرًا مباشرًا** في أودو (العملية لا تُسجّل)؛ دليله الوحيد
  غرفة الكاميرات. أثره غير المباشر: رصيد مخزون سالب + فروق جرد.
- فروق الكاش أغلبها «العدّ الختامي الفعلي = 0» (لم يُسجَّل) → فرق ظاهري، مش عجز حقيقي.
- قيود التدقيق الداخلي (uid 62, ref `SLX-*`) هي plugs تسوية — تُراجَع وتُعالَج، لا تُعتمد كحقيقة.
