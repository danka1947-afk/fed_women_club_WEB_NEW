## Phase 1 implementation notes

- Introduced unified button system classes: `.ui-button`, modifier variants (`--primary`, `--secondary`, `--ghost`, `--danger`, `--success`, `--disabled`), and size modifiers (`--sm`, `--md`, `--lg`, `--full`).
- Introduced shared action layout groups: `.ui-action-row`, `.ui-action-row--right`, `.ui-action-row--between`, `.ui-action-row--stack-mobile`, `.ui-card-actions`, `.ui-form-actions`, `.ui-toolbar-actions`.
- Backward compatibility aliases retained for admin inline actions: `.admin-inline-action--primary`, `.admin-inline-action--secondary`, `.admin-inline-action--danger` and `.admin-action-button` mapped visually to new UI button semantics.
- Action groups normalized in Admin/Partner/Client cards and media sections, including payment request cards and content review cards, by applying `ui-card-actions` / `ui-action-row` wrappers.
- Phase 2 TODO: deeper semantic review for ambiguous neutral actions (for example “Открыть партнёра” context priority) and broader refactor of legacy component-specific button selectors.
