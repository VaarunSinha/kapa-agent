# Kapa Demo

This project is a prototype that shows how an AI agent can act on reported documentation gaps and propose improvements through GitHub issues and pull requests.

The system analyzes a code repository, finds relevant files, generates research findings, and drafts documentation updates. Engineers can then review the proposed changes directly in a pull request.

## How it works

1. A documentation gap is reported through a GitHub issue.
2. The research processor analyzes the repository and identifies relevant files.
3. The system generates a findings report based on the code.
4. The writer agent drafts documentation updates.
5. A pull request is created with the proposed documentation and any open questions.

Contributors can review the changes, edit the draft, and answer questions directly in the pull request.

## Project structure

* **frontend**: Next.js interface for triggering documentation tasks
* **backend**: Django service that runs research and writer agents
* **docs**: Documentation site where the agent proposes changes

## Purpose

This demo simulates how an automated documentation assistant can help engineering teams respond to documentation gaps quickly and keep documentation aligned with the codebase.
