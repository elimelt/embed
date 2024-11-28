class EmbedManager {
  constructor () {
    this.defaultEmbedType = 'link'
    this.currentEmbedType = 'link'
    this.lastGeneratedData = null
    this.processingTime = null
    this.currentEmbedId = null
    this.embedKeys = JSON.parse(localStorage.getItem('embedKeys') || '{}')
    this.setupEventListeners()
    this.fetchAndRenderEmbedList()
    this.mdEditorRef = document.getElementById('markdown-input')
  }

  setupEventListeners () {
    // editor keyboard shortcuts
    document.addEventListener(
      'keydown',
      this.handleKeyboardShortcuts.bind(this)
    )

    // tab handling in editor
    const editor = document.getElementById('markdown-input')
    if (editor) {
      editor.addEventListener('keydown', this.handleEditorTab.bind(this))
      editor.addEventListener('input', this.adjustEditorHeight.bind(this))
      editor.addEventListener('keydown', this.preserveIndentation.bind(this))
    }
  }

  updateProcessingTime (time) {
    const badge = document.querySelector('.stats-badge span')
    this.processingTime = time
    badge.textContent = time ? `${time}ms` : '-- ms'
  }

  async createEmbed (content) {
    const startTime = performance.now()

    try {
      const response = await fetch('/api/embeds', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content })
      })

      const data = await response.json()
      this.lastGeneratedData = data
      this.currentEmbedId = data.uuid

      this.embedKeys[data.uuid] = data.auth_key
      localStorage.setItem('embedKeys', JSON.stringify(this.embedKeys))

      await this.fetchAndRenderEmbedList()

      const endTime = performance.now()
      this.updateProcessingTime(Math.round(endTime - startTime))

      return data
    } catch (error) {
      console.error('Failed to create embed:', error)
      throw error
    }
  }

  async updateEmbed (id, content) {
    const authKey = this.embedKeys[id]
    if (!authKey) {
      console.error('No authorization key found for this embed')
      return
    }

    try {
      await fetch(`/api/embeds/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: authKey
        },
        body: JSON.stringify({ content })
      })

      await this.fetchAndRenderEmbedList()
    } catch (error) {
      console.error('Failed to update embed:', error)
      throw error
    }
  }

  async deleteEmbed (id) {
    const authKey = this.embedKeys[id]
    if (!authKey) {
      console.error('No authorization key found for this embed')
      return
    }

    try {
      await fetch(`/api/embeds/${id}`, {
        method: 'DELETE',
        headers: {
          Authorization: authKey
        }
      })

      delete this.embedKeys[id]
      localStorage.setItem('embedKeys', JSON.stringify(this.embedKeys))

      if (this.currentEmbedId === id) {
        this.currentEmbedId = null
        document.getElementById('markdown-input').value = ''
      }

      await this.fetchAndRenderEmbedList()
    } catch (error) {
      console.error('Failed to delete embed:', error)
      throw error
    }
  }

  async fetchAndRenderEmbedList () {
    const container = document.getElementById('embed-list')
    if (!container) return

    const embedItems = []

    for (const [id, authKey] of Object.entries(this.embedKeys)) {
      try {
        const response = await fetch(`/api/embeds/${id}`, {
          headers: {
            Authorization: authKey
          }
        })

        if (!response.ok) {
          if (response.status === 404) {
            // document was deleted or expired, remove from local storage
            delete this.embedKeys[id]
            continue
          }
          throw new Error(`HTTP error! status: ${response.status}`)
        }

        const data = await response.json()
        embedItems.push({ id, content: data.content })
      } catch (error) {
        console.error(`Failed to fetch embed ${id}:`, error)
      }
    }

    localStorage.setItem('embedKeys', JSON.stringify(this.embedKeys))

    const html = embedItems
      .map(
        embed => `
        <div class="embed-item">
          <div class="flex justify-between items-center">
            <div class="text-sm text-gray-500">
              ID: ${embed.id.slice(0, 8)}...
            </div>
            <div class="embed-actions">
              <button onclick="embedManager.loadEmbed('${
                embed.id
              }')" class="embed-button edit-button">
                Edit
              </button>
              <button onclick="embedManager.deleteEmbed('${
                embed.id
              }')" class="embed-button delete-button">
                Delete
              </button>
            </div>
          </div>
          <div class="mt-2 font-mono text-sm text-gray-600">
            ${embed.content.slice(0, 100)}${
          embed.content.length > 100 ? '...' : ''
        }
          </div>
        </div>
      `
      )
      .join('')

    container.innerHTML =
      html || '<p class="text-gray-500 text-sm">No embeds yet</p>'
  }

  async loadEmbed (id) {
    const authKey = this.embedKeys[id]
    if (!authKey) {
      console.error('No authorization key found for this embed')
      return
    }

    try {
      const response = await fetch(`/api/embeds/${id}`, {
        headers: {
          Authorization: authKey
        }
      })

      if (!response.ok)
        throw new Error(`HTTP error! status: ${response.status}`)

      const data = await response.json()
      const editor = document.getElementById('markdown-input')
      editor.value = data.content
      this.currentEmbedId = id

      this.adjustEditorHeight({ target: editor })

      const preview = document.getElementById('preview')
      const embedCodeSection = document.getElementById('embed-code')
      this.updateEmbedCode(data)
      embedCodeSection.classList.remove('hidden')
      preview.classList.add('hidden')

      editor.focus()
    } catch (error) {
      console.error('Failed to load embed:', error)
    }
  }

  handleKeyboardShortcuts (e) {
    if ((e.ctrlKey || e.metaKey) && e.key === 'p') {
      e.preventDefault()
      this.previewMarkdown()
    }
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault()
      if (e.shiftKey) {
        this.generateNewEmbed() // Shift+Cmd+Enter creates new embed
      } else {
        this.saveOrUpdateEmbed() // Cmd+Enter saves/updates current embed
      }
    }
    if ((e.ctrlKey || e.metaKey) && e.key === 'c') {
      if (window.getSelection().toString()) return // don't prevent copying text
      e.preventDefault()
      if (this.currentEmbedType === 'iframe') {
        this.copyEmbed()
      } else {
        this.copyLink()
      }
    }
  }

  async saveOrUpdateEmbed () {
    const content = document.getElementById('markdown-input').value
    if (!content.trim()) return

    if (this.currentEmbedId) {
      await this.updateEmbed(this.currentEmbedId, content)
    } else {
      await this.generateNewEmbed()
    }
  }

  async generateNewEmbed () {
    const content = document.getElementById('markdown-input').value
    if (!content.trim()) return

    const startTime = performance.now()
    try {
      const data = await this.createEmbed(content)

      const preview = document.getElementById('preview')
      const embedCodeSection = document.getElementById('embed-code')

      this.updateEmbedCode(data)

      embedCodeSection.classList.remove('hidden')
      preview.classList.add('hidden')

      this.switchEmbedType(this.defaultEmbedType)

      const endTime = performance.now()
      this.updateProcessingTime(Math.round(endTime - startTime))
    } catch (error) {
      console.error('Embed generation failed:', error)
    }
  }

  handleEditorTab (e) {
    if (e.key === 'Tab') {
      e.preventDefault()

      const editor = e.target
      const start = editor.selectionStart
      const end = editor.selectionEnd
      const value = editor.value

      console.log('start:', start, 'end:', end)
      console.log('value:', value)

      if (e.shiftKey) {
        // handle shift+tab (remove indentation)
        if (start === end) {
          // single line
          const lineStart = value.lastIndexOf('\n', start - 1) + 1
          if (value.slice(lineStart, lineStart + 2) === '  ') {
            editor.value =
              value.slice(0, lineStart) + value.slice(lineStart + 2)
            editor.selectionStart = editor.selectionEnd = start - 2
          }
        } else {
          // multiple lines
          const lines = value.slice(start, end).split('\n')
          const newLines = lines.map(line =>
            line.startsWith('  ') ? line.slice(2) : line
          )
          const newText = newLines.join('\n')
          editor.value = value.slice(0, start) + newText + value.slice(end)
          editor.selectionStart = start
          editor.selectionEnd = start + newText.length
        }
      } else {
        // handle tab (add indentation)
        if (start === end) {
          // single line
          const spaces = '  '
          editor.value = value.slice(0, start) + spaces + value.slice(end)
          editor.selectionStart = editor.selectionEnd = start + 2
        } else {
          // multiple lines
          const lines = value.slice(start, end).split('\n')
          const newLines = lines.map(line => '  ' + line)
          const newText = newLines.join('\n')
          editor.value = value.slice(0, start) + newText + value.slice(end)
          editor.selectionStart = start
          editor.selectionEnd = start + newText.length
        }
      }
    }
  }

  adjustEditorHeight (e) {
    const editor = e.target
    editor.style.height = 'auto'
    editor.style.height = Math.max(256, editor.scrollHeight) + 'px'
  }

  preserveIndentation (e) {
    if (e.key === 'Enter') {
      const editor = e.target
      const start = editor.selectionStart
      const value = editor.value
      const lineStart = value.lastIndexOf('\n', start - 1) + 1
      const line = value.slice(lineStart, start)
      const indent = line.match(/^\s*/)[0]

      if (indent) {
        e.preventDefault()
        const newText = '\n' + indent
        editor.value =
          value.slice(0, start) + newText + value.slice(editor.selectionEnd)
        editor.selectionStart = editor.selectionEnd = start + newText.length
      }
    }
  }

  async previewMarkdown () {
    const content = document.getElementById('markdown-input').value
    if (!content.trim()) return

    const startTime = performance.now()
    try {
      const data = await this.createEmbed(content)
      const preview = document.getElementById('preview')
      const embedCode = document.getElementById('embed-code')

      preview.querySelector(
        '.preview-container'
      ).innerHTML = `<iframe src="${data.embed_url}" width="100%" height="400px" frameborder="0" class="rounded-lg"></iframe>`

      preview.classList.remove('hidden')
      embedCode.classList.add('hidden')

      const endTime = performance.now()
      this.updateProcessingTime(Math.round(endTime - startTime))
    } catch (error) {
      console.error('Preview failed:', error)
    }
  }

  async generateEmbed () {
    const content = document.getElementById('markdown-input').value
    if (!content.trim()) return

    const startTime = performance.now()
    try {
      const data = await this.createEmbed(content)
      const preview = document.getElementById('preview')
      const embedCodeSection = document.getElementById('embed-code')

      this.updateEmbedCode(data)

      embedCodeSection.classList.remove('hidden')
      preview.classList.add('hidden')

      this.switchEmbedType(this.defaultEmbedType)

      const endTime = performance.now()
      this.updateProcessingTime(Math.round(endTime - startTime))
    } catch (error) {
      console.error('Embed generation failed:', error)
    }
  }

  updateEmbedCode (data) {
    const iframeCode = `<iframe src="${window.location.origin}/embed/${data.uuid}" width="100%" height="500px" frameborder="0"></iframe>`
    const directLink = `${window.location.origin}/view/${data.uuid}`

    document.getElementById('embed-text').textContent = iframeCode
    document.getElementById('link-text').textContent = directLink
  }

  switchEmbedType (type) {
    this.currentEmbedType = type

    const iframeTab = document.getElementById('iframe-tab')
    const linkTab = document.getElementById('link-tab')
    const iframeContent = document.getElementById('iframe-content')
    const linkContent = document.getElementById('link-content')

    if (type === 'iframe') {
      iframeTab.classList.add('bg-gray-50')
      linkTab.classList.remove('bg-gray-50')
      iframeContent.classList.remove('hidden')
      linkContent.classList.add('hidden')
    } else {
      linkTab.classList.add('bg-gray-50')
      iframeTab.classList.remove('bg-gray-50')
      linkContent.classList.remove('hidden')
      iframeContent.classList.add('hidden')
    }
  }

  async copyEmbed () {
    await this.copyToClipboard(
      document.getElementById('embed-text').textContent,
      document.getElementById('copy-button')
    )
  }

  async copyLink () {
    await this.copyToClipboard(
      document.getElementById('link-text').textContent,
      document.getElementById('copy-link-button')
    )
  }

  async copyToClipboard (text, button) {
    try {
      const el = document.createElement('textarea')
      el.value = text
      document.body.appendChild(el)
      el.select()
      document.execCommand('copy')
      document.body.removeChild(el)

      const originalText = button.innerHTML
      button.innerHTML = `
        Copied
        <span class="keyboard-shortcut">
          <span class="key">⌘</span><span class="key">C</span>
        </span>
      `
      button.classList.add('text-green-600')

      setTimeout(() => {
        button.innerHTML = originalText
        button.classList.remove('text-green-600')
      }, 2000)
    } catch (error) {
      console.error('Failed to copy to clipboard:', error)
    }
  }
}

// singleton
let embedManager
document.addEventListener('DOMContentLoaded', () => {
  embedManager = new EmbedManager()
})
