---
sidebar_position: 1
title: Introduction
---

# Introduction

**Kapa Content Gap Action Agent** is an AI-powered documentation assistant that turns coverage gaps into actionable documentation updates. The system follows a defined pipeline: from identified gaps through research, questions, proposed fixes, review, and pull requests.

## What it does

The workflow runs as follows:

1. **Coverage gap**: Conversations or analytics surface where documentation is missing, unclear, or outdated. A coverage gap is recorded with a finding and suggestion.
2. **Issue**: Acting on a gap creates a GitHub-oriented issue (title, description, research goal). The Issue Creator agent drafts this from the gap and repo context.
3. **Research**: The Research Agent gathers relevant documentation and code context, analyzes it, and produces a research report. It may ask clarifying questions before concluding.
4. **Questions**: When the agent needs input, it emits questions (e.g., choice or free text). Answers are submitted and research can continue or conclude.
5. **Fix**: The Writer Agent produces documentation changes (one or more files) aligned with the project’s style. A fix is created and can be edited in the UI before review.
6. **Review**: Engineers review the proposed fix. Edits can be made via the Fix Assistant in the UI.
7. **Pull request**: Once approved, the backend publishes the fix to a branch and opens a PR; the original issue can be linked and commented on.

Engineers merge the PR when ready. The pipeline keeps documentation aligned with both the code and user feedback without manual discovery of every affected file.

## Who it's for

This tool is intended for engineering teams that:

- Maintain product or API documentation alongside their code
- Have a way to detect documentation gaps (e.g., conversation analytics, support tickets)
- Want to go from “we need docs for X” to a concrete, reviewable proposal quickly

## Scope

Kapa Demo is a **prototype**. It demonstrates the full flow: coverage gap → issue → research → questions → fix → review → PR. It is suitable for evaluation, internal demos, and as a base for a production-ready documentation assistant.

For setup, architecture, and API details, see the rest of this documentation set.
