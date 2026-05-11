const API_BASE_URL = 'http://127.0.0.1:8000';
let students = [];
let currentView = 'dashboard';

// DOM Elements
const sidebarItems = document.querySelectorAll('.sidebar-nav li');
const toast = document.getElementById('toast');

document.addEventListener('DOMContentLoaded', () => {
    setupNavigation();
    updateStats();
    setupStudentManagement();
    setupDetection();
    setupExcelImport();
    startTimeUpdate();
});

function startTimeUpdate() {
    const timeEl = document.getElementById('current-time-display');
    const update = () => {
        const now = new Date();
        if (timeEl) {
            timeEl.textContent = `Hệ thống đang sẵn sàng | ${now.toLocaleTimeString('vi-VN')} - ${now.toLocaleDateString('vi-VN')}`;
        }
    };
    setInterval(update, 1000);
    update();
}

function setupNavigation() {
    sidebarItems.forEach(item => {
        item.addEventListener('click', () => {
            const viewId = item.getAttribute('data-view');
            sidebarItems.forEach(i => i.classList.remove('active'));
            item.classList.add('active');
            switchView(viewId);
        });
    });
}

function switchView(viewId) {
    const allViews = document.querySelectorAll('.view');
    allViews.forEach(view => {
        if (view.id === `view-${viewId}`) {
            view.classList.remove('hidden');
            view.classList.add('active');
            if (viewId === 'students') loadStudents();
            if (viewId === 'fees') loadFees();
            if (viewId === 'dashboard') updateDashboard();
            if (viewId === 'logs') loadLogs();
        } else {
            view.classList.add('hidden');
            view.classList.remove('active');
        }
    });
    currentView = viewId;
}

// Student Management
async function loadStudents() {
    const studentsBody = document.getElementById('students-body');
    if (!studentsBody) return;
    try {
        const response = await fetch(`${API_BASE_URL}/admin/students`);
        const data = await response.json();
        students = data;
        renderStudents(data);
    } catch (error) {
        console.error('Error loading students:', error);
    }
}

function renderStudents(dataList) {
    const studentsBody = document.getElementById('students-body');
    if (!studentsBody) return;
    studentsBody.innerHTML = '';
    if (dataList.length === 0) {
        studentsBody.innerHTML = '<tr><td colspan="6" style="text-align: center; padding: 40px;">Không tìm thấy dữ liệu</td></tr>';
        return;
    }
    dataList.forEach(student => {
        const vehicle = student.vehicles && student.vehicles[0] ? student.vehicles[0] : null;
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${student.student_code}</td>
            <td>${student.full_name}</td>
            <td>${student.class_name}</td>
            <td>${vehicle ? (vehicle.vehicle_type === 'MOTORBIKE' ? 'Xe máy' : 'Xe đạp') : '---'}</td>
            <td>${vehicle ? (vehicle.license_plate || vehicle.tag_id || '---') : '---'}</td>
            <td>
                <button class="btn-action edit" onclick="editStudent('${student.id}')"><i class="fas fa-edit"></i></button>
                <button class="btn-action delete" onclick="deleteStudent('${student.id}')"><i class="fas fa-trash"></i></button>
            </td>
        `;
        studentsBody.appendChild(tr);
    });
}

// AI Detection Logic - WebRTC with 2s Auto Scan
function setupDetection() {
    const video = document.getElementById('webcam-feed-img');
    const canvas = document.getElementById('detection-canvas');
    const placeholder = document.getElementById('detection-placeholder');
    const btnStart = document.getElementById('btn-start-camera');
    const btnStop = document.getElementById('btn-stop-camera');
    const btnCapture = document.getElementById('btn-capture-ai'); // Manual capture (optional)

    const lightTop = document.getElementById('light-top');
    const lightBottom = document.getElementById('light-bottom');
    const mainStatusCard = document.getElementById('main-status-card');
    const statusText = document.getElementById('status-text');
    const statusDesc = document.getElementById('status-desc');
    const quickResult = document.getElementById('quick-result');

    let isStreaming = false;
    let autoScanInterval = null;

    if (!btnStart) return;

    btnStart.onclick = () => {
        const streamUrl = `${API_BASE_URL}/camera/stream?t=${new Date().getTime()}`;
        if (video) {
            video.src = streamUrl;
            // Chỉ bắt đầu quét khi stream thực sự tải xong
            video.onload = () => {
                console.log('Camera stream connected');
                video.classList.remove('hidden');
                if (placeholder) placeholder.classList.add('hidden');
                isStreaming = true;
                startAutoScan();
                showNotification('Hệ thống giám sát đã sẵn sàng', 'success');
            };
            video.onerror = () => {
                console.error('Camera stream failed');
                showNotification('Không thể kết nối với camera. Kiểm tra lại server!', 'error');
            };
        }
        
        btnStart.classList.add('hidden');
        if (btnStop) btnStop.classList.remove('hidden');
        if (btnCapture) btnCapture.classList.remove('hidden');
        setSignal('idle');
    };

    btnStop.onclick = () => {
        isStreaming = false;
        stopAutoScan();
        if (video) {
            video.src = '';
            video.classList.add('hidden');
        }
        if (placeholder) placeholder.classList.remove('hidden');
        btnStart.classList.remove('hidden');
        if (btnStop) btnStop.classList.add('hidden');
        if (btnCapture) btnCapture.classList.add('hidden');
        setSignal('idle');
    };

    if (btnCapture) {
        btnCapture.onclick = () => captureAndDetect();
    }

    const btnReset = document.getElementById('btn-reset-camera');
    if (btnReset) {
        btnReset.onclick = async () => {
            const icon = btnReset.querySelector('i');
            if (icon) icon.classList.add('fa-spin');
            try {
                const response = await fetch(`${API_BASE_URL}/camera/reset`, { method: 'POST' });
                if (response.ok) {
                    showNotification('Đã khởi động lại hệ thống Camera', 'success');
                    // Tải lại stream nếu đang bật
                    if (isStreaming && video) {
                        video.src = `${API_BASE_URL}/camera/stream?t=${new Date().getTime()}`;
                    }
                }
            } catch (error) {
                showNotification('Lỗi khi reset camera', 'error');
            } finally {
                if (icon) icon.classList.remove('fa-spin');
            }
        };
    }

    let activePlate = null;
    let emptyFrameCount = 0;

    let isScanning = false;

    function startAutoScan() {
        if (isScanning) return;
        isScanning = true;
        runScanLoop();
    }

    async function runScanLoop() {
        if (!isScanning) return;
        
        if (currentView === 'detection' && isStreaming) {
            // Hiệu ứng đèn vàng khi đang xử lý
            setSignal('scanning'); 
            console.log("[AI] Đang quét khung hình...");
            await captureAndDetect();
        }
        
        // Đợi 1000ms (1 giây) để tránh quá tải CPU nhưng vẫn đảm bảo tính thời thực
        if (isScanning) {
            setTimeout(runScanLoop, 1000);
        }
    }

    function stopAutoScan() {
        isScanning = false;
        activePlate = null;
    }

    async function captureAndDetect() {
        if (!video || !canvas || !isStreaming) return;
        
        // Chỉ bắt đầu khi camera đã sẵn sàng
        if (video.naturalWidth === 0) return;

        return new Promise((resolve) => {
            // Tối ưu hóa: Giảm độ phân giải ảnh gửi đi (Max 640px)
            const scale = Math.min(1, 640 / video.naturalWidth);
            canvas.width = video.naturalWidth * scale;
            canvas.height = video.naturalHeight * scale;
            
            const ctx = canvas.getContext('2d');
            // Vẽ vào canvas để lấy Blob
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

            canvas.toBlob(async (blob) => {
                // Xóa canvas ngay sau khi lấy Blob để nó trong suốt trở lại
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                
                if (!blob) {
                    resolve();
                    return;
                }

                // Cập nhật ảnh chụp snapshot lên giao diện
                const snapshotImg = document.getElementById('ai-snapshot-img');
                if (snapshotImg) {
                    const imageUrl = URL.createObjectURL(blob);
                    snapshotImg.src = imageUrl;
                    // Giải phóng bộ nhớ sau khi ảnh load
                    snapshotImg.onload = () => URL.revokeObjectURL(imageUrl);
                }

                const formData = new FormData();
                formData.append('file', blob, 'auto_scan.jpg');

                try {
                    const response = await fetch(`${API_BASE_URL}/ai/detect`, {
                        method: 'POST',
                        body: formData
                    });
                    const data = await response.json();
                    handleDetectionResult(data);
                } catch (error) {
                    console.error('AI Service error:', error);
                }
                resolve();
            }, 'image/jpeg', 0.8);
        });
    }

    function handleDetectionResult(data) {
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        
        // Quan trọng: Xóa trắng canvas để nhìn xuyên qua thấy camera bên dưới
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        canvas.classList.remove('hidden');

        if (!data.results || data.results.length === 0) {
            emptyFrameCount++;
            if (emptyFrameCount >= 5) { 
                if (activePlate !== null) {
                    activePlate = null;
                    setSignal('idle');
                    updateStatusUI(null);
                }
            }
            return;
        }

        emptyFrameCount = 0;
        
        // Vẽ Khung và Chữ lên Canvas
        data.results.forEach(result => {
            if (result.bbox) {
                const [x1, y1, x2, y2] = result.bbox;
                const isOK = result.is_registered;
                const isPaid = result.is_paid;
                
                // Màu sắc: Xanh (Đã đóng), Vàng (Chưa đóng), Đỏ (Chưa đăng ký)
                let color = '#ef4444'; // Mặc định Đỏ
                if (isOK) {
                    color = isPaid ? '#10b981' : '#f59e0b';
                }
                
                // Vẽ khung chính
                ctx.strokeStyle = color;
                ctx.lineWidth = 6;
                ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);
                
                // Vẽ hiệu ứng góc (Glow)
                ctx.shadowBlur = 15;
                ctx.shadowColor = color;
                ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);
                ctx.shadowBlur = 0;

                // Vẽ nhãn văn bản
                if (result.license_plate) {
                    ctx.fillStyle = color;
                    ctx.font = 'bold 24px Inter';
                    const statusText = isOK ? (isPaid ? 'ĐÃ ĐÓNG PHÍ' : 'CHƯA ĐÓNG PHÍ!') : 'CHƯA ĐĂNG KÝ';
                    const labelText = `${result.license_plate} - ${statusText}`;
                    const textWidth = ctx.measureText(labelText).width;
                    
                    ctx.fillRect(x1, y1 - 35, textWidth + 10, 30);
                    ctx.fillStyle = 'white';
                    ctx.fillText(labelText, x1 + 5, y1 - 12);
                }
            }
        });

        const result = data.results[0];
        const currentPlate = result.license_plate;

        // Chỉ cập nhật khi có biển số MỚI hoặc trạng thái thay đổi
        if (currentPlate && (currentPlate !== activePlate)) {
            activePlate = currentPlate;
            updateStatusUI(result);
            showNotification(`Phát hiện xe: ${currentPlate}`, result.is_registered ? 'success' : 'error');
        }
    }

    function updateStatusUI(result) {
        const resPlate = document.getElementById('res-plate-large');
        const resStatusBadge = document.getElementById('res-status-badge');
        const statusText = document.getElementById('status-text');
        const resName = document.getElementById('res-owner-name');
        const resClass = document.getElementById('res-owner-class');
        const resTime = document.getElementById('res-time');
        const resDate = document.getElementById('res-date');
        const resPaid = document.getElementById('res-payment-status');
        const alertMsg = document.getElementById('res-alert-msg');

        if (!result) {
            if (resPlate) resPlate.textContent = '-- -- --';
            if (resStatusBadge) {
                resStatusBadge.className = 'status-badge-modern';
                statusText.textContent = 'Đang chờ xe...';
            }
            if (resName) resName.textContent = 'Chưa rõ';
            if (resClass) resClass.textContent = '---';
            if (resPaid) resPaid.innerHTML = '---';
            if (alertMsg) alertMsg.textContent = '';
            setSignal('idle');
            return;
        }

        const isOK = result.is_registered;
        const isPaid = result.is_paid;
        const now = new Date();

        if (resPlate) resPlate.textContent = result.license_plate;
        if (resStatusBadge) {
            resStatusBadge.className = `status-badge-modern ${isOK ? 'registered' : 'unregistered'}`;
            statusText.textContent = isOK ? 'ĐÃ ĐĂNG KÝ' : 'CHƯA ĐĂNG KÝ';
        }
        if (resName) resName.textContent = result.owner ? result.owner.name : 'Vô danh / Khách';
        if (resClass) resClass.textContent = result.owner ? result.owner.class : 'N/A';
        if (resTime) resTime.textContent = now.toLocaleTimeString('vi-VN');
        if (resDate) resDate.textContent = now.toLocaleDateString('vi-VN');
        
        if (resPaid) {
            resPaid.innerHTML = isPaid ? 
                '<span class="status-badge status-paid">Đã đóng</span>' : 
                '<span class="status-badge status-pending">Chưa đóng!</span>';
        }
        
        if (alertMsg) {
            if (!isOK) {
                alertMsg.textContent = 'YÊU CẦU KIỂM TRA!';
                alertMsg.className = 'footer-alert error';
            } else if (!isPaid) {
                alertMsg.textContent = 'XE CHƯA ĐÓNG PHÍ!';
                alertMsg.className = 'footer-alert warning';
            } else {
                alertMsg.textContent = 'MỜI XE VÀO';
                alertMsg.className = 'footer-alert success';
            }
        }

        setSignal(isOK && isPaid ? 'success' : (isOK ? 'idle' : 'error'));
    }

    function setSignal(mode) {
        const lightTop = document.getElementById('light-top');
        const lightBottom = document.getElementById('light-bottom');
        if (!lightTop || !lightBottom) return;

        lightTop.classList.remove('active');
        lightBottom.classList.remove('active');

        if (mode === 'success') {
            lightBottom.classList.add('active'); // Đèn xanh ở dưới
        } else if (mode === 'error') {
            lightTop.classList.add('active'); // Đèn đỏ ở trên
        }
    }
}

// Dashboard Stats
async function updateDashboard() {
    try {
        const response = await fetch(`${API_BASE_URL}/admin/dashboard-stats`);
        const stats = await response.json();
        
        // Cập nhật các con số
        document.getElementById('total-students-count').textContent = stats.total_students;
        document.getElementById('total-motorbikes-count').textContent = stats.motorbikes;
        document.getElementById('total-bicycles-count').textContent = stats.bicycles;
        document.getElementById('paid-month-count').textContent = stats.paid_count;
        document.getElementById('unpaid-month-count').textContent = stats.unpaid_count;
        
        // Vẽ biểu đồ
        drawActivityChart(stats.activity_chart);
        
        // Cập nhật danh sách hoạt động mới nhất
        const recentList = document.getElementById('recent-activity-list');
        if (recentList) {
            recentList.innerHTML = '';
            if (stats.recent_logs.length === 0) {
                recentList.innerHTML = '<div class="empty-state">Chưa có hoạt động nào</div>';
            } else {
                stats.recent_logs.forEach(log => {
                    const item = document.createElement('div');
                    item.className = 'activity-item';
                    item.innerHTML = `
                        <div class="activity-time">${log.time}</div>
                        <div class="activity-info">
                            <div class="plate-mini">${log.plate}</div>
                            <div class="type-mini">${log.type === 'MOTORBIKE' ? 'Xe máy' : 'Xe đạp'}</div>
                        </div>
                    `;
                    recentList.appendChild(item);
                });
            }
        }
    } catch (error) {
        console.error('Lỗi khi cập nhật Dashboard:', error);
    }
}

function drawActivityChart(data) {
    const canvas = document.getElementById('activity-chart-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;
    ctx.clearRect(0, 0, width, height);
    
    const padding = 40;
    const chartW = width - padding * 2;
    const chartH = height - padding * 2;
    
    const maxVal = Math.max(...data.map(d => d.count), 5);
    
    // Vẽ lưới nền
    ctx.strokeStyle = '#f1f5f9';
    ctx.lineWidth = 1;
    for(let i=0; i<=5; i++) {
        const y = padding + (chartH / 5) * i;
        ctx.beginPath();
        ctx.moveTo(padding, y);
        ctx.lineTo(width - padding, y);
        ctx.stroke();
    }
    
    // Vẽ đường biểu đồ (Gradient)
    const gradient = ctx.createLinearGradient(0, padding, 0, height - padding);
    gradient.addColorStop(0, 'rgba(99, 102, 241, 0.2)');
    gradient.addColorStop(1, 'rgba(99, 102, 241, 0)');

    ctx.beginPath();
    ctx.strokeStyle = '#6366f1';
    ctx.lineWidth = 4;
    ctx.lineJoin = 'round';
    
    data.forEach((d, i) => {
        const x = padding + (chartW / (data.length - 1)) * i;
        const y = height - padding - (d.count / maxVal) * chartH;
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
    });
    ctx.stroke();
    
    // Vẽ vùng đổ màu dưới đường
    ctx.lineTo(width - padding, height - padding);
    ctx.lineTo(padding, height - padding);
    ctx.fillStyle = gradient;
    ctx.fill();
    
    // Vẽ các điểm nút
    data.forEach((d, i) => {
        const x = padding + (chartW / (data.length - 1)) * i;
        const y = height - padding - (d.count / maxVal) * chartH;
        
        ctx.fillStyle = '#fff';
        ctx.strokeStyle = '#6366f1';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.arc(x, y, 6, 0, Math.PI * 2);
        ctx.fill();
        ctx.stroke();
        
        // Hiển thị ngày
        ctx.fillStyle = '#64748b';
        ctx.font = 'bold 11px Inter';
        ctx.textAlign = 'center';
        ctx.fillText(d.date, x, height - 15);
        
        // Hiển thị số lượng trên đầu điểm
        ctx.fillStyle = '#1e293b';
        ctx.fillText(d.count, x, y - 12);
    });
}

async function updateStats() {
    try {
        const response = await fetch(`${API_BASE_URL}/admin/students`);
        const data = await response.json();
        students = data;

        document.getElementById('stat-total-students').textContent = data.length;

        let motorCount = 0;
        let bikeCount = 0;
        data.forEach(s => {
            if (s.vehicles) {
                s.vehicles.forEach(v => {
                    if (v.vehicle_type === 'MOTORBIKE') motorCount++;
                    else if (v.vehicle_type === 'BICYCLE') bikeCount++;
                });
            }
        });

        if (document.getElementById('stat-total-motor')) document.getElementById('stat-total-motor').textContent = motorCount;
        if (document.getElementById('stat-total-bike')) document.getElementById('stat-total-bike').textContent = bikeCount;
        if (document.getElementById('stat-total-paid')) document.getElementById('stat-total-paid').textContent = Math.floor(data.length * 0.85);
        if (document.getElementById('stat-total-unpaid')) document.getElementById('stat-total-unpaid').textContent = data.length - Math.floor(data.length * 0.85);

    } catch (error) {
        console.error('Error updating stats:', error);
    }
}

// Fee Management
async function loadFees() {
    const feesBody = document.getElementById('fees-body');
    if (!feesBody) return;
    try {
        const response = await fetch(`${API_BASE_URL}/admin/payment-status`);
        const data = await response.json();
        feesBody.innerHTML = '';
        
        let paidCount = 0;
        data.forEach(item => {
            if (item.is_paid) paidCount++;
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${item.student_code}</td>
                <td>${item.full_name}</td>
                <td>${item.class_name}</td>
                <td>${item.vehicle_type === 'MOTORBIKE' ? 'Xe máy' : 'Xe đạp'}</td>
                <td><span class="status-badge ${item.is_paid ? 'status-paid' : 'status-pending'}">${item.is_paid ? 'Đã đóng' : 'Chưa đóng'}</span></td>
                <td>
                    <button class="btn btn-sm ${item.is_paid ? 'btn-danger' : 'btn-primary'}" onclick="togglePayment('${item.id}')">
                        ${item.is_paid ? 'Hủy đóng' : 'Xác nhận đóng'}
                    </button>
                </td>
            `;
            feesBody.appendChild(tr);
        });
        
        drawPaymentChart(paidCount, data.length);
    } catch (error) {
        console.error('Error loading fees:', error);
    }
}

function drawPaymentChart(paid, total) {
    const canvas = document.getElementById('payment-summary-chart');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    const x = 20, y = 45, w = 150, h = 12;
    // Track
    ctx.fillStyle = '#e2e8f0';
    ctx.beginPath();
    if (ctx.roundRect) ctx.roundRect(x, y, w, h, 6); else ctx.rect(x, y, w, h);
    ctx.fill();
    
    // Progress
    const p = total > 0 ? (paid / total) * w : 0;
    ctx.fillStyle = '#10b981';
    ctx.beginPath();
    if (ctx.roundRect) ctx.roundRect(x, y, p, h, 6); else ctx.rect(x, y, p, h);
    ctx.fill();
    
    ctx.fillStyle = '#475569';
    ctx.font = 'bold 12px Inter';
    ctx.fillText(`THU PHÍ: ${paid}/${total}`, x, y - 10);
    ctx.fillText(`${total > 0 ? Math.round((paid/total)*100) : 0}%`, x + w + 10, y + 10);
}

window.togglePayment = async (studentId) => {
    try {
        const response = await fetch(`${API_BASE_URL}/admin/payments/${studentId}/toggle`, {
            method: 'POST'
        });
        if (response.ok) {
            showNotification('Đã cập nhật trạng thái phí', 'success');
            loadFees();
            updateStats();
        }
    } catch (error) {
        showNotification('Lỗi khi cập nhật phí', 'error');
    }
};

// Access Logs
async function loadLogs() {
    const logsBody = document.getElementById('logs-body');
    if (!logsBody) return;
    try {
        const response = await fetch(`${API_BASE_URL}/admin/access-logs`);
        const data = await response.json();
        logsBody.innerHTML = '';
        data.forEach(log => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${log.timestamp}</td>
                <td><img src="${API_BASE_URL}${log.image_path}" class="log-snapshot" onclick="window.open('${API_BASE_URL}${log.image_path}')" title="Click để phóng to"></td>
                <td>${log.vehicle_type === 'MOTORBIKE' ? 'Xe máy' : 'Xe đạp'}</td>
                <td><strong>${log.license_plate}</strong></td>
                <td>${log.full_name}</td>
                <td>
                    <span class="status-badge ${
                        log.status_text === 'Đã đóng phí' ? 'status-paid' : 
                        (log.status_text === 'Chưa đóng phí' ? 'status-pending' : 'status-unregistered')
                    }">${log.status_text}</span>
                </td>
            `;
            logsBody.appendChild(tr);
        });
    } catch (error) {
        console.error('Error loading logs:', error);
    }
}

// Student Management CRUD
let editingStudentId = null;
function setupStudentManagement() {
    const btnAdd = document.getElementById('btn-add-student');
    const modal = document.getElementById('modal-student');
    const form = document.getElementById('form-student');
    const btnClose = document.getElementById('btn-close-modal');
    if (!btnAdd || !modal || !form) return;
    btnAdd.onclick = () => {
        editingStudentId = null;
        form.reset();
        modal.querySelector('.modal-header h2').textContent = 'Thêm mới Học sinh & Xe';
        modal.classList.remove('hidden');
    };
    if (btnClose) btnClose.onclick = () => modal.classList.add('hidden');
    form.onsubmit = async (e) => {
        e.preventDefault();
        const studentData = {
            student_code: document.getElementById('student_code').value,
            full_name: document.getElementById('full_name').value,
            class_name: document.getElementById('class_name').value,
            vehicles: [{
                vehicle_type: document.getElementById('vehicle_type').value,
                license_plate: document.getElementById('license_plate').value || null,
                tag_id: document.getElementById('tag_id').value || null,
                brand: document.getElementById('brand').value,
                color: document.getElementById('color').value
            }]
        };
        try {
            const url = editingStudentId ? `${API_BASE_URL}/admin/students/${editingStudentId}` : `${API_BASE_URL}/admin/students`;
            const response = await fetch(url, {
                method: editingStudentId ? 'PUT' : 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(studentData)
            });
            if (response.ok) {
                showNotification('Lưu thành công', 'success');
                modal.classList.add('hidden');
                loadStudents();
                updateStats();
            }
        } catch (error) {
            showNotification('Lỗi máy chủ', 'error');
        }
    };
}

window.editStudent = (id) => {
    const student = students.find(s => s.id == id);
    if (!student) return;
    editingStudentId = id;
    const modal = document.getElementById('modal-student');
    modal.querySelector('.modal-header h2').textContent = 'Chỉnh sửa Học sinh & Xe';
    document.getElementById('student_code').value = student.student_code;
    document.getElementById('full_name').value = student.full_name;
    document.getElementById('class_name').value = student.class_name;
    if (student.vehicles && student.vehicles[0]) {
        const v = student.vehicles[0];
        document.getElementById('vehicle_type').value = v.vehicle_type;
        document.getElementById('license_plate').value = v.license_plate || '';
        document.getElementById('tag_id').value = v.tag_id || '';
        document.getElementById('brand').value = v.brand || '';
        document.getElementById('color').value = v.color || '';
    }
    modal.classList.remove('hidden');
};

window.deleteStudent = async (id) => {
    if (!confirm('Xóa học sinh này?')) return;
    try {
        await fetch(`${API_BASE_URL}/admin/students/${id}`, { method: 'DELETE' });
        loadStudents();
        updateStats();
    } catch (e) { }
};

function setupExcelImport() {
    const btnDownload = document.getElementById('btn-download-template');
    const excelUpload = document.getElementById('excel-upload');
    if (btnDownload) {
        btnDownload.onclick = async () => {
            const response = await fetch(`${API_BASE_URL}/admin/export-excel`);
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `mau_hoc_sinh.xlsx`;
            a.click();
        };
    }
    if (excelUpload) {
        excelUpload.onchange = async (e) => {
            const file = e.target.files[0];
            const formData = new FormData();
            formData.append('file', file);
            await fetch(`${API_BASE_URL}/ai/import-excel`, { method: 'POST', body: formData });
            loadStudents();
            updateStats();
            excelUpload.value = '';
        };
    }
}

function showNotification(message, type = 'info') {
    const toast = document.getElementById('toast');
    if (!toast) return;
    toast.textContent = message;
    toast.className = `toast ${type}`;
    toast.classList.remove('hidden');
    setTimeout(() => toast.classList.add('hidden'), 3000);
}
