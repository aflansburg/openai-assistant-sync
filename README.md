![update assistant status workflow](https://github.com/aflansburg/openai-assistant-sync/actions/workflows/update_assistant.yml/badge.svg)

### Purpose

Repository for assistant instruction & function definition version control.
Comes with automation to update your assistant on OpenAI.

### Dev guide

1. Create a directory for your assistant.
2. Create a a `config.yml` for your assistant config. If it already exists on OpenAI use its existing `id` and `name`. Otherwise, for a new assistant provide a name and keep the `id` blank. It will be populated by a commit from the Github Actions workflow that creates the assistant.
3. Provide functions in `functions` directory with a `.func.json` extension and a `prompt-template.md` file for your assistant's instructions in `/prompt-templates` directory. Functions use JSON Schema. OpenAI should support all [JSON Schema types](https://json-schema.org/understanding-json-schema/reference) for the most part.
4. Set a repository secret @ `https://github.com/your-profile-or-org/repo-name/settings/secrets/actions` for `OPENAI_API_KEY`.
