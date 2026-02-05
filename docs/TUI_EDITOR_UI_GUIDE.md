# TUI Editor UI Implementation - Visual Guide

This document describes the expected UI appearance and behavior after implementing the TUI Editor integration.

## Page Form View (Create/Edit Article Page)

### URL
- Create: `/dashboard/content/articles/{article_pk}/pages/create/`
- Edit: `/dashboard/content/articles/{article_pk}/pages/{page_pk}/edit/`

### Layout Structure

```
┌─────────────────────────────────────────────────────────────────┐
│ ← [Back Button]  Articles > Article Title > Content > Edit Page │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  [Edit/Create Page]                                             │
│  Update the content and details for this page.                  │
│                                                                  │
│  ┌──────────────────────┬──────────────────────┐               │
│  │ Page Number *        │ Title                │               │
│  │ [1              ]    │ [Optional page title]│               │
│  └──────────────────────┴──────────────────────┘               │
│                                                                  │
│  Content *                                                       │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ TUI EDITOR - Main Content                               │   │
│  │ ════════════════════════════════════════════════════════│   │
│  │ [B][I][S] [H] [•][1] [<>][{}] [Link][Image] [...]      │   │
│  │ ────────────────────────────────────────────────────────│   │
│  │ Markdown Editor      │  Live Preview                    │   │
│  │ # Introduction       │  Introduction                    │   │
│  │                      │  ═══════════                     │   │
│  │ This is **bold**     │  This is bold text               │   │
│  │ and *italic* text.   │  and italic text.                │   │
│  │                      │                                   │   │
│  │ - List item 1        │  • List item 1                   │   │
│  │ - List item 2        │  • List item 2                   │   │
│  │                      │                                   │   │
│  │ ```python            │  def hello():                    │   │
│  │ def hello():         │      print("Hello")              │   │
│  │     print("Hello")   │                                   │   │
│  │ ```                  │                                   │   │
│  │                      │                                   │   │
│  │ [600px height]       │                                   │   │
│  └─────────────────────────────────────────────────────────┘   │
│  Use Markdown format for rich content                           │
│                                                                  │
│  Preview Content                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ TUI EDITOR - Preview Content                            │   │
│  │ ════════════════════════════════════════════════════════│   │
│  │ [B][I] [•][1] [Link] [<>]                              │   │
│  │ ────────────────────────────────────────────────────────│   │
│  │ Markdown Editor      │  Live Preview                    │   │
│  │ **Preview** text     │  Preview text here...            │   │
│  │ here...              │                                   │   │
│  │                      │                                   │   │
│  │ [300px height]       │                                   │   │
│  └─────────────────────────────────────────────────────────┘   │
│  This content will be visible to users before purchase          │
│                                                                  │
│  ────────────────────────────────────────────────────────────  │
│  [Cancel]                                    [Update Page] →    │
└─────────────────────────────────────────────────────────────────┘
```

## Color Scheme (Dark Theme)

### Editor Components
- **Toolbar Background**: `#1a1a1a`
- **Editor Background**: `#0d0d0d`
- **Text Color**: `#e5e5e5`
- **Border**: `rgba(255, 255, 255, 0.1)`
- **Border Radius**: `0.5rem` (8px)

### Dashboard Integration
- **Card Background**: `bg-surface-dark` (dark gray)
- **Form Background**: `bg-surface-darker` (darker gray)
- **Primary Button**: Yellow/Gold gradient
- **Secondary Button**: Light gray
- **Text Primary**: White/Light gray
- **Text Muted**: Medium gray

## Editor Features

### Main Content Editor
- **Height**: 600px
- **Mode**: Markdown only (no WYSIWYG)
- **Preview**: Vertical split (side-by-side)
- **Toolbar Items**:
  - Heading levels (H1, H2, H3)
  - Bold, Italic, Strike
  - HR, Quote
  - Lists (UL, OL, Task)
  - Indent/Outdent
  - Table, Image, Link
  - Code, Code block
  - Scroll Sync

### Preview Content Editor
- **Height**: 300px
- **Mode**: Markdown only
- **Preview**: Vertical split
- **Toolbar Items** (Simplified):
  - Heading, Bold, Italic
  - Lists (UL, OL)
  - Link
  - Code

## Internationalization

### Language Selection
Language is automatically detected from `request.LANGUAGE_CODE`:

**French (fr)**
```
Editor UI en français
- "Gras" (Bold)
- "Italique" (Italic)
- "Liste" (List)
- etc.
```

**Spanish (es)**
```
Editor UI en español
- "Negrita" (Bold)
- "Cursiva" (Italic)
- "Lista" (List)
- etc.
```

**English (en)**
```
Editor UI in English (default)
- "Bold"
- "Italic"
- "List"
- etc.
```

## Responsive Design

### Desktop (≥1024px)
- Full side-by-side editor and preview
- All toolbar items visible
- Optimal editing experience

### Tablet (768px - 1023px)
- Editor and preview stacked or side-by-side
- Toolbar may wrap to multiple lines
- Still fully functional

### Mobile (<768px)
- Editor and preview stacked vertically
- Toolbar items may be grouped or hidden
- Touch-optimized

## User Interactions

### 1. Creating a New Page
```
User clicks "Add Page" → 
  Form loads with empty editors →
    User enters page number and title →
      User types markdown in content editor →
        Preview updates in real-time →
          User optionally adds preview content →
            User clicks "Create Page" →
              Markdown is saved to database
```

### 2. Editing an Existing Page
```
User clicks "Edit" on a page card →
  Form loads with existing content in editors →
    Editor displays saved markdown →
      Preview shows rendered content →
        User makes changes →
          Preview updates in real-time →
            User clicks "Update Page" →
              Updated markdown is saved
```

### 3. Form Submission
```
User clicks "Create/Update Page" →
  JavaScript captures markdown from both editors →
    Markdown is written to hidden textareas →
      Form submits normally →
        Django view receives markdown strings →
          Markdown is saved to ArticlePage.content fields
```

## Expected Behavior

### ✅ Working Features
- [x] Dark theme matches dashboard
- [x] Real-time markdown preview
- [x] Toolbar in user's language
- [x] Syntax highlighting for code blocks
- [x] Table editing
- [x] Image and link insertion
- [x] Scroll synchronization between editor and preview
- [x] Form validation (required fields)
- [x] Auto-save markdown on form submit

### ✅ SEO Optimizations
When markdown is rendered with `{{ content|markdown_to_html }}`:
- [x] Proper heading hierarchy (h1, h2, h3)
- [x] Semantic HTML5 tags
- [x] Table of contents generation
- [x] Smart typography (quotes, dashes)
- [x] Clean, minimal markup

## Testing Scenarios

### Test 1: Basic Markdown
1. Create a new page
2. Enter markdown with headers, bold, italic
3. Verify preview shows formatted text
4. Save and reload
5. Verify content is preserved

### Test 2: Code Blocks
1. Enter a code block with syntax
2. Verify syntax highlighting in preview
3. Save and reload
4. Verify code is preserved with formatting

### Test 3: Tables
1. Create a markdown table
2. Verify table renders in preview
3. Save and reload
4. Verify table structure is preserved

### Test 4: Internationalization
1. Change browser/Django language to French
2. Create a new page
3. Verify editor UI is in French
4. Repeat for Spanish and English

### Test 5: Dark Theme
1. Open page form
2. Verify editor has dark background
3. Verify toolbar has dark background
4. Verify text is light colored
5. Verify scrollbars are styled

## Screenshots Needed

When testing, capture screenshots of:

1. ✅ **Full Page Form View** - Showing both editors with content
2. ✅ **Content Editor Closeup** - Showing markdown and preview side-by-side
3. ✅ **Preview Editor Closeup** - Showing the smaller preview editor
4. ✅ **French UI** - Editor with French language
5. ✅ **Spanish UI** - Editor with Spanish language
6. ✅ **Dark Theme Details** - Showing scrollbars, borders, colors
7. ✅ **Form Validation** - Error states for required fields
8. ✅ **Rendered Output** - How markdown displays after `markdown_to_html` filter

## Implementation Files

### Modified Files
1. `tech_articles/templates/tech-articles/dashboard/pages/content/articles/manage/page_form.html`
   - TUI Editor integration
   - Dark theme CSS
   - JavaScript initialization
   - i18n support

2. `tech_articles/templates/tech-articles/dashboard/pages/content/articles/manage/content.html`
   - Fixed duplicate scripts
   - Added conditional i18n loading

3. `tech_articles/content/templatetags/markdown_filters.py`
   - Markdown to HTML filter
   - Markdown to plain text filter

4. `pyproject.toml`
   - Added markdown==3.7 dependency

### New Files
1. `tech_articles/content/templatetags/__init__.py`
2. `tech_articles/content/templatetags/README.md`
3. `docs/TUI_EDITOR_SAMPLES.md`

## Next Steps for User

1. ✅ Install dependencies: `uv sync` or `pip install markdown==3.7`
2. ✅ Start development server
3. ✅ Navigate to article management
4. ✅ Create or edit an article page
5. ✅ Test the TUI Editor with sample content
6. ✅ Verify markdown is saved correctly
7. ✅ Test different languages
8. ✅ Capture screenshots for documentation
