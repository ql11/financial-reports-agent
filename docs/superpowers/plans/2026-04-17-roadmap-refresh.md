# PROJECT_ROADMAP Refresh Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rewrite `PROJECT_ROADMAP.md` into a new execution-oriented roadmap centered on extraction robustness, while preserving the previous optimization cycle as archived history.

**Architecture:** This change is documentation-only. The implementation replaces the current roadmap structure with three clearly separated parts: archived baseline, current execution cycle, and non-current future directions. The rewritten file must follow the approved design spec and avoid mixing historical accomplishments with current work items.

**Tech Stack:** Markdown, Git, PowerShell

---

### Task 1: Rewrite The Roadmap Structure

**Files:**
- Modify: `PROJECT_ROADMAP.md`
- Reference: `docs/superpowers/specs/2026-04-17-roadmap-refresh-design.md`
- Test: `PROJECT_ROADMAP.md`

- [ ] **Step 1: Read the approved design and current roadmap**

Run:

```powershell
Get-Content -Raw docs/superpowers/specs/2026-04-17-roadmap-refresh-design.md
Get-Content -Raw PROJECT_ROADMAP.md
```

Expected: both files open successfully, and the approved structure is available before editing.

- [ ] **Step 2: Replace the roadmap with the new structure**

Write `PROJECT_ROADMAP.md` so it contains these top-level sections in order:

```markdown
# 项目路线图

## 文档用途

## 历史基线：上一轮已完成优化（归档）

## 当前轮次：提取鲁棒性优先

## 下一轮执行路线图

### 阶段 A：解析稳定性与版式抗扰动

### 阶段 B：字段覆盖与证据完整性

### 阶段 C：验证体系与回归资产扩充

## 后续阶段（非本轮）

### 分析能力深化

### 产品化推进

## 维护规则
```

When writing the body:

- move previous accomplishments into the archived baseline section grouped by capability area;
- keep the current cycle focused only on extraction robustness;
- give each execution phase these four subsections:
  - `目标`
  - `关键任务`
  - `完成标准`
  - `风险与依赖`
- keep future work in the non-current section only;
- remove the old rolling checklist style from the main execution body.

- [ ] **Step 3: Review the rewritten roadmap for structure and scope**

Run:

```powershell
Get-Content -Raw PROJECT_ROADMAP.md
```

Verify all of the following:

- the archived baseline is present and contains the previous optimization cycle;
- the current cycle is explicitly named `提取鲁棒性优先`;
- the execution body contains exactly three near-term phases;
- analysis-depth and productization items are only in the future section;
- the document ends with maintenance rules that describe how to update the roadmap later.

- [ ] **Step 4: Inspect the diff to confirm this is a documentation-only restructure**

Run:

```powershell
git diff -- PROJECT_ROADMAP.md
```

Expected: only `PROJECT_ROADMAP.md` changes, and the diff shows a reorganization toward archived baseline plus execution plan.

- [ ] **Step 5: Commit**

```powershell
git add PROJECT_ROADMAP.md
git commit -m "docs: refresh roadmap for extraction robustness cycle"
```
