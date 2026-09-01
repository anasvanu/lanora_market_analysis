/**
 * Lanora Gold Trading LLC — AI Market Studio Frontend Controller
 * Handles live PDF streaming, multi-recipient dispatch, and AI Prompt commands.
 */

let CURRENT_STATE = null;
let ACTIVE_VIEW_MODE = 'pdf'; // 'pdf' | 'slides'
let ACTIVE_SLIDE_INDEX = 1;

// ==========================================================================
// Initialization
// ==========================================================================
document.addEventListener('DOMContentLoaded', () => {
  fetchMarketData();
});

// ==========================================================================
// View Switcher (PDF Preview vs Interactive Slides)
// ==========================================================================
function setViewMode(mode) {
  ACTIVE_VIEW_MODE = mode;
  const pdfPane = document.getElementById('pdfViewerPane');
  const slidesPane = document.getElementById('slidesViewerPane');
  const btnPdf = document.getElementById('btnViewPdf');
  const btnSlides = document.getElementById('btnViewSlides');

  if (mode === 'pdf') {
    pdfPane.classList.remove('hidden');
    slidesPane.classList.add('hidden');
    btnPdf.classList.add('active');
    btnSlides.classList.remove('active');
  } else {
    pdfPane.classList.add('hidden');
    slidesPane.classList.remove('hidden');
    btnPdf.classList.remove('active');
    btnSlides.classList.add('active');
  }
}

function switchSlide(index) {
  ACTIVE_SLIDE_INDEX = index;
  document.querySelectorAll('.slide').forEach(s => s.classList.remove('active'));
  document.querySelectorAll('.slide-tab').forEach(t => t.classList.remove('active'));

  const targetSlide = document.getElementById(`slide-${index}`);
  if (targetSlide) targetSlide.classList.add('active');

  const tabs = document.querySelectorAll('.slide-tab');
  if (tabs[index - 1]) tabs[index - 1].classList.add('active');
}

// ==========================================================================
// API: Fetch & Sync Market Data State
// ==========================================================================
async function fetchMarketData() {
  try {
    const res = await fetch('/api/data', { cache: 'no-store' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    CURRENT_STATE = await res.json();
    updateUIWithState(CURRENT_STATE);
  } catch (err) {
    console.error('Failed to fetch market data:', err);
    showToast('Failed to fetch market data from server.', 'error');
  }
}

function updateUIWithState(data) {
  if (!data) return;

  const g = data.gold;
  const s = data.silver;
  const meta = data.report_metadata;
  const co = data.company;

  // Header Tickers
  const topGold = document.getElementById('topGoldSpot');
  const topSilver = document.getElementById('topSilverSpot');
  if (topGold) topGold.textContent = `$${g.spot.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  if (topSilver) topSilver.textContent = `$${s.spot.toFixed(3)}`;

  // Slide 1: Cover
  setElemText('s1Firm', co.name);
  setElemText('s1Date', meta.date);
  setElemText('s1Loc', co.location);
  setElemText('s1SpotRef', `$${g.spot.toFixed(2)}`);

  // Slide 2: Macro Calendar
  const tbody = document.getElementById('macroTableBody');
  if (tbody && data.macro_calendar) {
    tbody.innerHTML = data.macro_calendar.map(ev => `
      <tr>
        <td><strong>${ev.time}</strong></td>
        <td><span class="badge-cur">${ev.currency}</span></td>
        <td>${ev.event}</td>
        <td><strong>${ev.forecast}</strong></td>
        <td>${ev.previous}</td>
      </tr>
    `).join('');
  }

  // Slide 3: Gold Matrix
  setElemText('s3GoldSpot', `$${g.spot.toFixed(2)}`);
  setElemText('s3GoldPivot', `$${g.pivots.P.toFixed(2)}`);
  setElemText('s3GoldR1', `$${g.pivots.R1.toFixed(2)}`);
  setElemText('s3GoldS1', `S1: ${g.pivots.S1.toFixed(2)}`);
  setElemText('s3GoldS2', `S2: ${g.pivots.S2.toFixed(2)}`);
  setElemText('s3GoldS3', `S3: ${g.pivots.S3.toFixed(2)}`);
  setElemText('s3GoldR1Row', `R1: ${g.pivots.R1.toFixed(2)}`);
  setElemText('s3GoldR2', `R2: ${g.pivots.R2.toFixed(2)}`);
  setElemText('s3GoldR3', `R3: ${g.pivots.R3.toFixed(2)}`);
  setElemText('s3BuyTitle', `📈 ${g.trade_plan.buy.trigger}`);
  setElemText('s3BuyBody', `Targets: ${g.trade_plan.buy.target1} | ${g.trade_plan.buy.target2}\nStop Loss: ${g.trade_plan.buy.stop_loss}`);
  setElemText('s3SellTitle', `📉 ${g.trade_plan.sell.trigger}`);
  setElemText('s3SellBody', `Targets: ${g.trade_plan.sell.target1} | ${g.trade_plan.sell.target2}\nStop Loss: ${g.trade_plan.sell.stop_loss}`);

  // Slide 4: Silver Matrix
  setElemText('s4SilverSpot', `$${s.spot.toFixed(3)}`);
  setElemText('s4SilverPivot', `$${s.pivots.P.toFixed(3)}`);
  setElemText('s4SilverR1', `$${s.pivots.R1.toFixed(3)}`);
  setElemText('s4SilverS1', `S1: ${s.pivots.S1.toFixed(3)}`);
  setElemText('s4SilverS2', `S2: ${s.pivots.S2.toFixed(3)}`);
  setElemText('s4SilverS3', `S3: ${s.pivots.S3.toFixed(3)}`);
  setElemText('s4SilverR1Row', `R1: ${s.pivots.R1.toFixed(3)}`);
  setElemText('s4SilverR2', `R2: ${s.pivots.R2.toFixed(3)}`);
  setElemText('s4SilverR3', `R3: ${s.pivots.R3.toFixed(3)}`);
  setElemText('s4BuyTitle', `📈 ${s.trade_plan.buy.trigger}`);
  setElemText('s4BuyBody', `Targets: ${s.trade_plan.buy.target1} / ${s.trade_plan.buy.target2} | SL: ${s.trade_plan.buy.stop_loss}`);
  setElemText('s4SellTitle', `📉 ${s.trade_plan.sell.trigger}`);
  setElemText('s4SellBody', `Targets: ${s.trade_plan.sell.target1} / ${s.trade_plan.sell.target2} | SL: ${s.trade_plan.sell.stop_loss}`);

  // Slide 5: Closing
  setElemText('s5Phone', co.phone);
  setElemText('s5Email', `${co.email}\n${co.social}`);

  // Update chart images with cache buster
  const gImg = document.getElementById('slideGoldChartImg');
  if (gImg) gImg.src = `assets/gold_chart.png?t=${Date.now()}`;
  const sImg = document.getElementById('slideSilverChartImg');
  if (sImg) sImg.src = `assets/silver_chart.png?t=${Date.now()}`;
}

function setElemText(id, text) {
  const elem = document.getElementById(id);
  if (elem) elem.innerText = text;
}

// ==========================================================================
// PDF Management (Reload, Rebuild, Fullscreen)
// ==========================================================================
function refreshPdfFrame() {
  const frame = document.getElementById('pdfFrame');
  if (frame) {
    frame.src = `/api/pdf?t=${Date.now()}`;
    showToast('PDF frame reloaded.', 'info');
  }
}

async function generateAndReloadPdf() {
  showToast('⚡ Rebuilding PDF report with current data...', 'info');
  try {
    const res = await fetch('/api/generate-pdf', { method: 'POST' });
    const data = await res.json();
    if (data.success) {
      refreshPdfFrame();
      showToast(`✅ PDF Successfully Generated (${data.timestamp})`, 'success');
    } else {
      showToast('⚠️ PDF generation returned an error.', 'error');
    }
  } catch (err) {
    console.error('Error generating PDF:', err);
    showToast(`Error generating PDF: ${err.message}`, 'error');
  }
}

function openPdfNewTab() {
  window.open(`/api/pdf?t=${Date.now()}`, '_blank');
}

async function resetToLiveMarket() {
  showToast('🔄 Refetching live market spot data...', 'info');
  try {
    const res = await fetch('/api/reset-data', { method: 'POST' });
    const data = await res.json();
    if (data.success) {
      CURRENT_STATE = data.data;
      updateUIWithState(CURRENT_STATE);
      refreshPdfFrame();
      showToast('✅ Reset to live spot quotes successfully!', 'success');
      appendAiBubble('🔄 Reset all data to live market spot quotes and regenerated the PDF report.');
    }
  } catch (err) {
    showToast('Error resetting to live data.', 'error');
  }
}

// ==========================================================================
// AI Prompt Studio Controller
// ==========================================================================
async function submitAiPrompt(event) {
  if (event) event.preventDefault();
  const input = document.getElementById('aiPromptInput');
  const promptText = input.value.trim();
  if (!promptText) return;

  // Append user bubble
  appendUserBubble(promptText);
  input.value = '';

  const btnSend = document.getElementById('btnSendPrompt');
  if (btnSend) btnSend.disabled = true;

  try {
    const res = await fetch('/api/ai-command', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: jsonStringifySafe({ prompt: promptText })
    });
    const result = await res.json();

    if (result.success) {
      CURRENT_STATE = result.data;
      updateUIWithState(CURRENT_STATE);
      refreshPdfFrame();
      appendAiBubble(result.message);
      showToast('✨ AI modifications applied to report & PDF!', 'success');
    } else {
      appendAiBubble(`⚠️ ${result.error || 'Failed to process command.'}`);
    }
  } catch (err) {
    appendAiBubble(`❌ Error communicating with AI Studio server: ${err.message}`);
  } finally {
    if (btnSend) btnSend.disabled = false;
  }
}

function handlePromptKeydown(event) {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault();
    submitAiPrompt();
  }
}

function applyQuickPrompt(promptText) {
  const input = document.getElementById('aiPromptInput');
  if (input) {
    input.value = promptText;
    submitAiPrompt();
  }
}

function appendUserBubble(text) {
  const chat = document.getElementById('chatViewport');
  if (!chat) return;

  const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  const bubble = document.createElement('div');
  bubble.className = 'chat-bubble user-bubble';
  bubble.innerHTML = `
    <div class="bubble-header">
      <span class="user-tag">YOU</span>
      <span class="time-tag">${timeStr}</span>
    </div>
    <div class="bubble-body">${escapeHtml(text)}</div>
  `;
  chat.appendChild(bubble);
  chat.scrollTop = chat.scrollHeight;
}

function appendAiBubble(text) {
  const chat = document.getElementById('chatViewport');
  if (!chat) return;

  const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  const formattedHtml = formatAiMarkdown(text);

  const bubble = document.createElement('div');
  bubble.className = 'chat-bubble ai-bubble';
  bubble.innerHTML = `
    <div class="bubble-header">
      <span class="bot-tag">LANORA AI</span>
      <span class="time-tag">${timeStr}</span>
    </div>
    <div class="bubble-body">${formattedHtml}</div>
  `;
  chat.appendChild(bubble);
  chat.scrollTop = chat.scrollHeight;
}

function clearChatHistory() {
  const chat = document.getElementById('chatViewport');
  if (chat) {
    chat.innerHTML = '';
    appendAiBubble('🧹 Chat history cleared. Ready for your next command!');
  }
}

function formatAiMarkdown(text) {
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/\n/g, '<br>');
}

function escapeHtml(str) {
  return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function jsonStringifySafe(obj) {
  return JSON.stringify(obj);
}

// ==========================================================================
// Multi-Channel Dispatch (Email & WhatsApp)
// ==========================================================================
async function dispatchEmail() {
  const input = document.getElementById('emailInput');
  const recipients = input ? input.value.trim() : '';
  if (!recipients) {
    showToast('Please enter at least one recipient email address.', 'error');
    return;
  }

  const btn = document.getElementById('btnSendEmail');
  const btnText = document.getElementById('emailBtnText');
  if (btn) btn.disabled = true;
  if (btnText) btnText.textContent = '⏳ Sending Email...';

  showToast(`📧 Dispatching PDF report to: ${recipients}...`, 'info');

  try {
    const res = await fetch('/api/dispatch-email', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ recipients })
    });
    const result = await res.json();

    if (result.status === 'SENT_SMTP_SUCCESS') {
      showToast(`✅ Email successfully delivered to ${result.count} recipient(s)!`, 'success');
      appendAiBubble(`📧 **Email Dispatch Confirmed:** Delivered PDF report to **${result.recipients.join(', ')}**.`);
    } else if (result.status === 'SENT_SIMULATED') {
      showToast(`ℹ️ Email dispatch logged (Simulated): ${result.recipients.join(', ')}`, 'info');
      appendAiBubble(`ℹ️ **Email Logged:** ${result.note}\nRecipients: *${result.recipients.join(', ')}*`);
    } else {
      showToast(`⚠️ Email dispatch: ${result.error || result.status}`, 'error');
    }
  } catch (err) {
    showToast(`Failed to send email: ${err.message}`, 'error');
  } finally {
    if (btn) btn.disabled = false;
    if (btnText) btnText.textContent = '📧 Send Email Report';
  }
}

async function dispatchWhatsApp() {
  const input = document.getElementById('whatsappInput');
  const phone = input ? input.value.trim() : '';
  if (!phone) {
    showToast('Please enter a WhatsApp phone number.', 'error');
    return;
  }

  const btn = document.getElementById('btnSendWhatsapp');
  const btnText = document.getElementById('waBtnText');
  if (btn) btn.disabled = true;
  if (btnText) btnText.textContent = '⏳ Sending...';

  showToast(`📱 Dispatching WhatsApp report to ${phone}...`, 'info');

  try {
    const res = await fetch('/api/dispatch-whatsapp', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ phone })
    });
    const result = await res.json();

    if (result.status === 'SENT_WEBHOOK_SUCCESS') {
      showToast(`✅ WhatsApp message delivered to ${result.phone}!`, 'success');
      appendAiBubble(`📱 **WhatsApp Dispatch Confirmed:** Sent daily technical summary to **${result.phone}**.`);
    } else if (result.status === 'SENT_SIMULATED') {
      showToast(`ℹ️ WhatsApp summary logged for: ${result.phone}`, 'info');
      appendAiBubble(`📱 **WhatsApp Summary Prepared for ${result.phone}:**\n\`\`\`\n${result.message}\n\`\`\``);
    } else {
      showToast(`⚠️ WhatsApp: ${result.error || result.status}`, 'error');
    }
  } catch (err) {
    showToast(`WhatsApp dispatch error: ${err.message}`, 'error');
  } finally {
    if (btn) btn.disabled = false;
    if (btnText) btnText.textContent = '📱 Send WhatsApp';
  }
}

// ==========================================================================
// Toast Notifications
// ==========================================================================
function showToast(message, type = 'info') {
  const container = document.getElementById('toastContainer');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `<span>${message}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(12px)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}
