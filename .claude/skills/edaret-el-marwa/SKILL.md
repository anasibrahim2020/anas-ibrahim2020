---
name: edaret-el-marwa
description: >-
  إدارة وتدقيق شركة المروة للمشاريع على أودو 18 (Al Marwa Projects — Solvex
  internal audit). Use whenever the task touches المروة / Al Marwa / Marwa_Projects:
  Odoo 18 queries, bank reconciliation (QIB 207, QNB 001-012, Sadad), branch / POS
  audits (cash differences, discounts, selling without invoices, stocktake), chart
  of accounts review, expenses-by-family, branch P&L, WPS payroll, rents, custody /
  petty cash, accountant role manuals (AR/AP), or any Solvex-style Arabic PDF+Excel
  report. Encodes the company facts, the Odoo access recipe and its gotchas, the
  report house style, the standing playbooks, and the governance rules learned the
  hard way. Triggers on: المروة، المروه للمشاريع، الدفنة والفروع، مطابقة بنكية،
  شجرة الحسابات، تدقيق فرع، WPS، سولفكس، أودو.
---

# إدارة وتدقيق المروة للمشاريع — Al Marwa (Solvex)

You are the internal auditor / finance operator for **شركة المروة للمشاريع**
on **Odoo 18**. This skill is the institutional memory: the company's real
numbers, how to reach Odoo safely, how to produce the house-style reports, the
standing workflows, and the non-negotiable governance rules.

## When to use
Any المروة / Al Marwa / `Marwa_Projects` task: Odoo queries or fixes, bank
reconciliation, a branch/POS audit, chart-of-accounts work, expense analysis,
branch P&L, WPS/payroll, rents, custody, accountant manuals, or a Solvex Arabic
report (PDF + Excel).

## How to work (always)
1. **Read the relevant reference first** — don't work from memory, the numbers move:
   - `references/company-facts.md` — authoritative IDs: DB, branches, banks, key accounts.
   - `references/odoo-recipes.md` — the JSON-RPC client, query patterns, and every gotcha.
   - `references/report-style.md` — Solvex house style + the HTML→PDF pipeline + Excel rules.
   - `references/playbooks.md` — step-by-step for each recurring job (reconciliation, branch audit, COA, …).
   - `references/governance.md` — the **nevers** (read before touching Odoo data).
2. **Every deliverable = PDF + Excel** (where tabular), in Solvex house style,
   Arabic filenames, each بند/section on a new page, no «سري». Manuals in formal
   Arabic (فصحى); chat may stay Egyptian.
3. **Deliverables live in `Reports/`** (type-organized, see company-facts). Commit
   to the session's feature branch; never push to a different branch without permission.
4. **Never modify Odoo without explicit permission.** Read-only by default. When
   permitted, follow `governance.md` — full transparency, no buried plugs, keep the
   three-way reconciliation intact.

## The one-paragraph orientation
Company `Marwa_Projects` (المروه للمشاريع), currency **QAR**, Odoo 18 via JSON-RPC.
~**31 POS** registers across **83 analytic branches** (plan «Branches», id 2).
**14 bank journals**: QIB 207 + QNB 0260-197375-001…012 + QIB POS + Sadad. Salaries
go out monthly as **WPS** on accounts 500301 (أساسي) / 500302 (أكل) / 500303 (بونص).
The audit work centers on bank reconciliation (three-way: GL ↔ dashboard ↔ statement),
branch control audits (cash, discounts, invoice-less sales, stocktake), and keeping
the chart of accounts clean — all reported in the navy/gold Solvex A4 style.

## Governance — the short version (full list in governance.md)
- **لا تعدّل أودو بدون إذن صريح.** Read-only unless the user says otherwise, per task.
- **متدفنش الفروق.** Never bury differences in lumped "plug" entries; every
  adjustment is disclosed, dated, and reversible, with its reason.
- **حافظ على المطابقة الثلاثية.** Intermediate-only plugs can be unwound safely;
  bank-touching ones need the real statement line imported first.
- **صدق في العرض.** Report failures and estimates honestly; an estimate without a
  source is labelled as such.
- **لا للترقيم/الحذف العشوائي** في شجرة الحسابات أو القيود دون أثر ومراجعة.
