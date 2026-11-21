---
name: skill-creator
description: Create new skills, modify and improve existing skills, and measure skill performance. Use when users want to create a skill from scratch, edit, or optimize an existing skill, run evals to test a skill, benchmark skill performance with variance analysis, or optimize a skill's description for better triggering accuracy.
---

# Skill Creator

A skill for creating new skills and iteratively improving them.

At a high level, the process of creating a skill goes like this:

- Decide what you want the skill to do and roughly how it should do it
- Write a draft of the skill
- Create a few test prompts and run claude-with-access-to-the-skill on them
- Help the user evaluate the results both qualitatively and quantitatively
- Rewrite the skill based on feedback from the user's evaluation of the results
- Repeat until you're satisfied
- Expand the test set and try again at larger scale

Your job when using this skill is to figure out where the user is in this process and then jump in and help them progress through these stages.

---

## Creating a skill

### Capture Intent

Start by understanding the user's intent. The current conversation might already contain a workflow the user wants to capture (e.g., they say "turn this into a skill"). If so, extract answers from the conversation history first.

1. What should this skill enable Claude to do?
2. When should this skill trigger? (what user phrases/contexts)
3. What's the expected output format?
4. Should we set up test cases to verify the skill works?

### Write the SKILL.md

Based on the user interview, fill in these components:

- **name**: Skill identifier
- **description**: When to trigger, what it does. Make descriptions a little "pushy" — include both what the skill does AND specific contexts for when to use it.
- **compatibility**: Required tools, dependencies (optional)
- **the rest of the skill**

### Skill Writing Guide

#### Anatomy of a Skill

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter (name, description required)
│   └── Markdown instructions
└── Bundled Resources (optional)
    ├── scripts/    - Executable code for deterministic/repetitive tasks
    ├── references/ - Docs loaded into context as needed
    └── assets/     - Files used in output (templates, icons, fonts)
```

#### Progressive Disclosure

Skills use a three-level loading system:
1. **Metadata** (name + description) - Always in context (~100 words)
2. **SKILL.md body** - In context whenever skill triggers (<500 lines ideal)
3. **Bundled resources** - As needed (unlimited)

#### Writing Patterns

- Keep SKILL.md under 500 lines
- Reference files clearly from SKILL.md with guidance on when to read them
- Use imperative form in instructions
- Explain the **why** behind instructions — don't just issue MUSTs
- Keep the prompt lean; remove things that aren't pulling their weight

---

## Running and evaluating test cases

### Step 1: Spawn all runs (with-skill AND baseline) in the same turn

For each test case, spawn two subagents in the same turn — one with the skill, one without.

**With-skill run:**
```
Execute this task:
- Skill path: <path-to-skill>
- Task: <eval prompt>
- Save outputs to: <workspace>/iteration-<N>/eval-<ID>/with_skill/outputs/
```

**Baseline run:** same prompt, no skill path, save to `without_skill/outputs/`.

### Step 2: While runs are in progress, draft assertions

Draft quantitative assertions for each test case. Good assertions are objectively verifiable and have descriptive names. Update `evals/evals.json` with the assertions once drafted.

### Step 3: Capture timing data

When each subagent task completes, save timing data to `timing.json`:

```json
{
  "total_tokens": 84852,
  "duration_ms": 23332,
  "total_duration_seconds": 23.3
}
```

### Step 4: Grade, aggregate, and launch the viewer

1. **Grade each run** — spawn a grader subagent that evaluates each assertion against the outputs. Save results to `grading.json`.

2. **Aggregate into benchmark:**
   ```bash
   python -m scripts.aggregate_benchmark <workspace>/iteration-N --skill-name <name>
   ```

3. **Launch the viewer:**
   ```bash
   nohup python <skill-creator-path>/eval-viewer/generate_review.py \
     <workspace>/iteration-N \
     --skill-name "my-skill" \
     --benchmark <workspace>/iteration-N/benchmark.json \
     > /dev/null 2>&1 &
   ```
   For headless environments: use `--static <output_path>` to write a standalone HTML file.

4. Tell the user: "I've opened the results in your browser. 'Outputs' lets you click through each test case and leave feedback, 'Benchmark' shows the quantitative comparison."

### Step 5: Read the feedback

When the user is done, read `feedback.json`. Empty feedback means the user thought it was fine. Focus improvements on test cases where the user had specific complaints.

---

## Improving the skill

### How to think about improvements

1. **Generalize from the feedback.** Create skills that work across many different prompts, not just the test examples. Avoid overly specific or narrow instructions.

2. **Keep the prompt lean.** Remove things that aren't pulling their weight.

3. **Explain the why.** Explain reasoning so the model understands why something is important — more effective than rigid ALWAYS/NEVER rules.

4. **Look for repeated work across test cases.** If all test cases resulted in similar helper scripts, bundle that script in `scripts/` once.

### The iteration loop

After improving the skill:

1. Apply improvements to the skill
2. Rerun all test cases into a new `iteration-<N+1>/` directory
3. Launch the reviewer with `--previous-workspace` pointing at the previous iteration
4. Wait for the user to review and give feedback
5. Read feedback, improve again, repeat

Keep going until the user is happy, all feedback is empty, or you're not making meaningful progress.

---

## Description Optimization

The description field determines whether Claude invokes a skill. After creating or improving a skill, offer to optimize it.

### Generate trigger eval queries

Create 20 eval queries — a mix of should-trigger and should-not-trigger. Queries must be realistic and specific (include file paths, company names, context). The negative cases should be genuinely tricky near-misses, not obviously irrelevant.

### Run the optimization loop

```bash
python -m scripts.run_loop \
  --eval-set <path-to-trigger-eval.json> \
  --skill-path <path-to-skill> \
  --model <model-id-powering-this-session> \
  --max-iterations 5 \
  --verbose
```

Apply `best_description` from the JSON output to update the skill's frontmatter.

---

## Claude.ai / Cowork adaptations

**No subagents (Claude.ai):** Run test cases one at a time, present results inline, skip quantitative benchmarking. Description optimization requires `claude` CLI — skip on Claude.ai.

**Cowork:** Use `--static <output_path>` for the viewer (no browser). "Submit All Reviews" downloads `feedback.json` as a file.

**Updating an existing skill:** Preserve the original name and directory. Copy to a writeable location before editing.

---

## Core loop summary

1. Figure out what the skill is about
2. Draft or edit the skill
3. Run claude-with-access-to-the-skill on test prompts
4. With the user, evaluate the outputs (viewer + quantitative evals)
5. Repeat until satisfied
6. Package the final skill and return it to the user
