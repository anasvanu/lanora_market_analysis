/**
 * Lanora Gold Trading LLC — Report Runner Controller
 */

document.addEventListener('DOMContentLoaded', () => {
  fetchStatus();
});

async function fetchStatus() {
  try {
    const res = await fetch('/api/data');
    if (res.ok) {
      const data = await res.json();
      document.getElementById('valGoldSpot').innerText = `$${data.gold.spot.toFixed(2)}`;
      document.getElementById('valSilverSpot').innerText = `$${data.silver.spot.toFixed(3)}`;
    }
  } catch (e) {
    console.warn('Status fetch error:', e);
  }
}

async function runReportJob() {
  const btn = document.getElementById('btnRunJob');
  const statusElem = document.getElementById('jobStatusText');

  btn.disabled = true;
  statusElem.innerText = '⏳ Running Job (Fetching Live Spot & Generating PDF)...';
  statusElem.style.color = '#dfb256';
  showToast('⚡ Running Daily Report Job...', 'info');

  try {
    // 1. Reset & fetch live data
    await fetch('/api/reset-data', { method: 'POST' });
    
    // 2. Re-generate PDF
    const res = await fetch('/api/generate-pdf', { method: 'POST' });
    const data = await res.json();

    if (data.success) {
      statusElem.innerText = `● Job Completed Successfully (${data.timestamp})`;
      statusElem.style.color = '#22c55e';
      showToast('✅ Daily Technical Report Generated Successfully!', 'success');
      reloadPreview();
      fetchStatus();
    } else {
      statusElem.innerText = '⚠️ Job encountered an issue';
      statusElem.style.color = '#ef4444';
      showToast('PDF generation returned an error.', 'error');
    }
  } catch (err) {
    statusElem.innerText = '❌ Job execution failed';
    statusElem.style.color = '#ef4444';
    showToast(`Error running job: ${err.message}`, 'error');
  } finally {
    btn.disabled = false;
  }
}

function reloadPreview() {
  const frame = document.getElementById('pdfFrame');
  if (frame) {
    frame.src = `/api/pdf?t=${Date.now()}`;
    showToast('Preview frame refreshed.', 'info');
  }
}

function openFullscreen() {
  window.open(`/api/pdf?t=${Date.now()}`, '_blank');
}

async function sendMail() {
  const input = document.getElementById('emailRecipients');
  const recipients = input ? input.value.trim() : '';
  if (!recipients) {
    showToast('Please enter recipient email(s).', 'error');
    return;
  }

  const btn = document.getElementById('btnMail');
  btn.disabled = true;
  showToast(`📧 Sending PDF to ${recipients}...`, 'info');

  try {
    const res = await fetch('/api/dispatch-email', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ recipients })
    });
    const result = await res.json();
    if (result.status === 'SENT_SMTP_SUCCESS') {
      showToast(`✅ Email successfully sent to ${result.count} recipient(s)!`, 'success');
    } else if (result.status === 'SENT_SIMULATED') {
      showToast(`ℹ️ Email dispatch logged: ${result.recipients.join(', ')}`, 'info');
    } else {
      showToast(`⚠️ Email: ${result.error || result.status}`, 'error');
    }
  } catch (err) {
    showToast(`Error sending email: ${err.message}`, 'error');
  } finally {
    btn.disabled = false;
  }
}

async function sendWhatsApp() {
  const input = document.getElementById('waPhone');
  const phone = input ? input.value.trim() : '';
  if (!phone) {
    showToast('Please enter a WhatsApp phone number.', 'error');
    return;
  }

  const btn = document.getElementById('btnWa');
  btn.disabled = true;
  showToast(`📱 Sending WhatsApp to ${phone}...`, 'info');

  try {
    const res = await fetch('/api/dispatch-whatsapp', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ phone })
    });
    const result = await res.json();
    if (result.status === 'SENT_WEBHOOK_SUCCESS') {
      showToast(`✅ WhatsApp sent to ${result.phone}!`, 'success');
    } else {
      showToast(`ℹ️ WhatsApp logged for ${result.phone}`, 'info');
    }
  } catch (err) {
    showToast(`Error: ${err.message}`, 'error');
  } finally {
    btn.disabled = false;
  }
}

function showToast(message, type = 'info') {
  const container = document.getElementById('toastContainer');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.innerText = message;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(12px)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}
