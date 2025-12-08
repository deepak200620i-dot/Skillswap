# SkillSwap - User Search & Chat Features Demo Guide

## 🔍 User Search by Name - How to Use

### Backend Endpoint

```
GET /api/matching/search-users
```

### Example 1: Search by Name

```bash
curl -X GET "http://localhost:5000/api/matching/search-users?q=john" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**

```json
{
  "users": [
    {
      "id": 2,
      "full_name": "John Smith",
      "email": "john.smith@example.com",
      "bio": "Python developer interested in web development",
      "profile_picture": "https://ui-avatars.com/api/?name=JS&background=random",
      "location": "New York",
      "availability": "Available weekends",
      "review_count": 3,
      "avg_rating": 4.7,
      "created_at": "2025-12-01T10:00:00"
    }
  ],
  "count": 1
}
```

### Example 2: Search by Location

```bash
curl -X GET "http://localhost:5000/api/matching/search-users?location=California" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Example 3: Combined Search

```bash
curl -X GET "http://localhost:5000/api/matching/search-users?q=jane&location=California&limit=5" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 💬 Chat Features - Visual Layout

### Desktop View (> 1200px)

```
┌──────────────────────────────────────────────────────────────────┐
│ SkillSwap Navigation Bar                                         │
├──────────────────────────────┬──────────────────────────────────┤
│ Conversations (350px)        │ Messages Panel (Flex)            │
├──────────────────────────────┼──────────────────────────────────┤
│ Messages                     │ [Avatar] John Doe     [📞] [ℹ️]  │
│ [🔍 Search conversations]   ├──────────────────────────────────┤
│                              │                                  │
│ ┌──────────────────────────┐ │ [Other's message]               │
│ │ [Avatar] Jane Doe        │ │                                  │
│ │ Jane Doe                 │ │ Hey! How are you?               │
│ │ Thanks for your help...  │ │ 10:30 AM                        │
│ │ 10:45 AM         [3]     │ │                                  │
│ └──────────────────────────┘ │ [Your message - Right aligned]   │
│                              │ I'm doing great! How about you?  │
│ ┌──────────────────────────┐ │ 10:32 AM                        │
│ │ [Avatar] John Smith      │ │                                  │
│ │ John Smith               │ │ [Other's message]               │
│ │ Got your message...      │ │                                  │
│ │ 09:15 AM                 │ │ Perfect! Let's chat sometime    │
│ └──────────────────────────┘ │ 10:33 AM                        │
│                              ├──────────────────────────────────┤
│                              │ [Type a message...] 😊 [➤ Send] │
│                              │ (Auto-expanding textarea)        │
└──────────────────────────────┴──────────────────────────────────┘
```

### Tablet View (769px - 1200px)

```
┌───────────────┬────────────────────────────────────┐
│ Conversations │ Messages Panel                     │
│ (280px)       ├────────────────────────────────────┤
│               │ [Avatar] John Doe     [📞] [ℹ️]    │
├───────────────┼────────────────────────────────────┤
│ Messages      │ [Other's message]                  │
│ [🔍 Search]   │ How are you?                       │
│               │ 10:30 AM                           │
│ ┌───────────┐ │                                    │
│ │ [Avatar]  │ │ [Your message - Right]             │
│ │ Jane      │ │ I'm great! You?                    │
│ │ Thanks... │ │ 10:32 AM                           │
│ └───────────┘ │                                    │
│               ├────────────────────────────────────┤
│ ┌───────────┐ │ [Type...] 😊 [➤]                  │
│ │ [Avatar]  │ │
│ │ John      │ │
│ │ Got your..│ │
│ └───────────┘ │
```

### Mobile View (< 768px)

```
┌──────────────────────────────┐
│ Messages [🔍 Search]         │
├──────────────────────────────┤
│ [Horizontal Scrolling List]  │
│ ┌─────┐ ┌─────┐ ┌─────┐     │
│ │Jane │ │John │ │Sarah│ ... │
│ │ 👤  │ │ 👤  │ │ 👤  │     │
│ │ 3   │ │ 1   │ │ 0   │     │
│ └─────┘ └─────┘ └─────┘     │
├──────────────────────────────┤
│ [Avatar] John Doe     [📞][ℹ️]│
├──────────────────────────────┤
│                              │
│ [Other's message]            │
│ How are you?                 │
│ 10:30 AM                     │
│                              │
│ [Your message - Right]       │
│ I'm great! You?              │
│ 10:32 AM                     │
│                              │
├──────────────────────────────┤
│ [Type a message...]  😊 [➤]  │
│ (Auto-expanding)             │
└──────────────────────────────┘
```

---

## 😊 Emoji Feature - Step by Step

### Adding Emoji to Message

1. **Click Emoji Button**

   - Located in message input area (😊 button)
   - Position: Left of Send button

2. **Emoji Inserted**

   - Random emoji from preset list appears
   - Input auto-focuses
   - Textarea expands if needed

3. **Type More**

   - Add additional text after emoji
   - Textarea auto-expands up to 120px
   - Shift+Enter for new line

4. **Send Message**
   - Press Enter (Cmd+Enter on Mac) or click Send
   - Message appears with emoji preserved

### Available Emojis (Sample)

```
Smileys: 😀 😃 😄 😁 😆 😅 🤣 😂 😊 😇 🙂 🙃 😉
Hearts:  ❤️ 🧡 💛 💚 💙 💜
Gestures: 👍 👎 👋 ✋ 👌
Celebrations: 🎉 🎊 🎈 ✨ 🔥 ⭐
```

---

## 🎨 Chat UI Color Scheme

### Message Styling

```
Incoming Messages:
- Background: #e5e7eb (Light Gray)
- Text Color: #1f2937 (Dark Gray)
- Border Radius: 12px with 4px bottom-left

Outgoing Messages:
- Background: #6366f1 (Indigo - Primary Color)
- Text Color: White
- Border Radius: 12px with 4px bottom-right
```

### Interface Colors

```
Primary: #6366f1 (Indigo)
Hover: #4f46e5 (Darker Indigo)
Background: #f9fafb (Light Gray)
Borders: #e0e0e0 (Medium Gray)
Text: #1f2937 (Dark Gray)
Muted: #6b7280 (Gray)
```

---

## ⌨️ Keyboard Shortcuts

| Shortcut      | Action                 |
| ------------- | ---------------------- |
| Enter         | Send message           |
| Shift + Enter | New line in message    |
| Cmd/Ctrl + A  | Select all text        |
| Esc           | Clear input (optional) |

---

## 📱 Responsive Breakpoints

```
Mobile:    0px - 768px
Tablet:    769px - 1200px
Desktop:   1200px+
```

### Layout Changes

- **Mobile**: Conversations show as horizontal list, messages below
- **Tablet**: Narrow sidebar (280px), wider message area
- **Desktop**: Full sidebar (350px), spacious message area

---

## 🔐 Security Features

- All messages encrypted with Fernet (AES-256)
- JWT token authentication required
- Input sanitization with HTML escaping
- User isolation (can only chat with authorized users)
- Rate limiting on chat endpoints (1 per second)

---

## 🚀 Performance Tips

1. **Lazy Loading**: Messages load incrementally
2. **Debounced Search**: Prevents excessive database queries
3. **Auto-refresh**: Every 3 seconds for new messages
4. **Efficient Rendering**: Only updated elements re-render
5. **Smooth Animations**: GPU-accelerated CSS transforms

---

## 🐛 Troubleshooting

### Issue: Emoji button not working

**Solution**: Ensure JavaScript is enabled and browser supports ES6

### Issue: Chat layout broken on mobile

**Solution**: Check viewport meta tag: `<meta name="viewport" content="width=device-width, initial-scale=1.0">`

### Issue: Messages not auto-scrolling

**Solution**: Clear browser cache and refresh, check console for errors

### Issue: Search returns no results

**Solution**: Verify search query syntax, check user email/name spelling

---

## 📊 API Rate Limits

```
Chat Endpoints: 1 request per second
Search Endpoint: No limit (server-side limiting recommended)
Auth Endpoints: 10/day signup, 50/hour login
```

---

**Version**: 1.0
**Last Updated**: December 9, 2025
**Status**: Production Ready
