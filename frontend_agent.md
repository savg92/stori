# Frontend Agent Instructions

## Tech Stack
- **Language**: TypeScript
- **Framework**: React + Vite
- **Styling**: TailwindCSS + Shadcn UI
- **Charts**: Recharts
- **State Management**: React Query
- **Testing**: Vitest + Playwright

## Rules
- Components ≤150 lines (target 100).
- Each component: single responsibility, split into subcomponents/hooks if too large.
- **Dark mode by default** (must match PRD).
- Use strict TypeScript typing for props and state.
- Validate all forms/inputs before submission.
- Optimize for **mobile-first** (min 320px).
- Test every major feature (unit + integration).

## File Structure
```
src/components/[FeatureName]/
├── [FeatureName].tsx
├── [FeatureName].types.ts
├── [FeatureName].test.tsx
├── hooks/
├── utils/
└── styles/
```

## Quality Checklist
- [ ] Code linted (ESLint + Prettier).  
- [ ] All components <150 lines.  
- [ ] Accessibility verified.  
- [ ] Responsive on mobile.  
- [ ] Dark mode working.  
