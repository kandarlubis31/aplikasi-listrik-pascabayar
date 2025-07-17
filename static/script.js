document.addEventListener('DOMContentLoaded', () => {

    // --- Flash message close button and auto-hide ---
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(message => {
        setTimeout(() => {
            message.style.opacity = '0';
            message.style.transform = 'translateY(-20px)';
            setTimeout(() => message.remove(), 500);
        }, 5000);

        const closeBtn = message.querySelector('.flash-close-btn');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                message.style.opacity = '0';
                message.style.transform = 'translateY(-20px)';
                setTimeout(() => message.remove(), 500);
            });
        }
    });

    // --- Login Form Logic ---
    const togglePassword = document.getElementById('togglePassword');
    const passwordInput = document.getElementById('password');

    if (togglePassword && passwordInput) {
        togglePassword.addEventListener('click', () => {
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);
            togglePassword.classList.toggle('fa-eye-slash');
            togglePassword.setAttribute('aria-label', type === 'password' ? 'Tampilkan password' : 'Sembunyikan password');
        });
    }

    const loginForm = document.getElementById('loginForm');
    const usernameInput = document.getElementById('username');
    const usernameError = document.getElementById('username-error');
    const passwordError = document.getElementById('password-error');
    const submitLoginBtn = document.getElementById('submitLoginBtn');
    const loadingSpinner = submitLoginBtn ? submitLoginBtn.querySelector('.loading-spinner') : null;

    if (loginForm) {
        loginForm.addEventListener('submit', function (event) {
            let isValid = true;

            if (usernameInput.value.trim() === '') {
                usernameError.textContent = 'Username tidak boleh kosong.';
                usernameInput.classList.add('input-error');
                isValid = false;
            } else {
                usernameError.textContent = '';
                usernameInput.classList.remove('input-error');
            }

            if (passwordInput.value.trim() === '') {
                passwordError.textContent = 'Password tidak boleh kosong.';
                passwordInput.classList.add('input-error');
                isValid = false;
            } else {
                passwordError.textContent = '';
                passwordInput.classList.remove('input-error');
            }

            if (!isValid) {
                event.preventDefault();
            } else {
                if (submitLoginBtn) {
                    submitLoginBtn.disabled = true;
                    if (loadingSpinner) {
                        loadingSpinner.style.display = 'inline-block';
                    }
                }
            }
        });

        if (usernameInput) {
            usernameInput.addEventListener('input', function () {
                if (this.value.trim() === '') {
                    usernameError.textContent = 'Username tidak boleh kosong.';
                    this.classList.add('input-error');
                } else {
                    usernameError.textContent = '';
                    this.classList.remove('input-error');
                }
            });
        }

        if (passwordInput) {
            passwordInput.addEventListener('input', function () {
                if (this.value.trim() === '') {
                    passwordError.textContent = 'Password tidak boleh kosong.';
                    this.classList.add('input-error');
                } else {
                    passwordError.textContent = '';
                    this.classList.remove('input-error');
                }
            });
        }
    }

    // --- Payment Form Multi-Step Logic (bayar_tagihan.html) ---
    const paymentForm = document.getElementById('paymentForm');
    if (paymentForm) {
        const step1 = document.getElementById('step1');
        const step2 = document.getElementById('step2');
        const nextStepBtn = document.getElementById('nextStepBtn');
        const prevStepBtn = document.getElementById('prevStepBtn');
        const totalBayarInput = document.getElementById('total_bayar');
        const biayaAdminInput = document.getElementById('biaya_admin');
        const progressSteps = document.querySelectorAll('.progress-step');

        function updateProgress(currentStep) {
            progressSteps.forEach(step => {
                const stepNum = parseInt(step.dataset.step);
                if (stepNum === currentStep) {
                    step.classList.add('active');
                } else {
                    step.classList.remove('active');
                }
            });
        }

        if (nextStepBtn) {
            nextStepBtn.addEventListener('click', () => {
                step1.style.display = 'none';
                step2.style.display = 'block';
                totalBayarInput.focus();
                updateProgress(2);
            });
        }

        if (prevStepBtn) {
            prevStepBtn.addEventListener('click', () => {
                step2.style.display = 'none';
                step1.style.display = 'block';
                updateProgress(1);
            });
        }

        updateProgress(1);

        const totalTagihanFinalElement = paymentForm.dataset.totalTagihanFinal;
        if (totalTagihanFinalElement) {
            const totalTagihanFinal = parseFloat(totalTagihanFinalElement);
            const biayaAdmin = parseFloat(biayaAdminInput.value);

            if (!isNaN(totalTagihanFinal) && !isNaN(biayaAdmin)) {
                totalBayarInput.value = (totalTagihanFinal + biayaAdmin).toFixed(2);
            }
        }
    }

    // --- Admin Penggunaan Form Logic (admin_penggunaan_form.html) ---
    const adminPenggunaanForm = document.getElementById("adminPenggunaanForm");
    const submitAdminBtn = document.getElementById("submitBtn");

    if (adminPenggunaanForm && submitAdminBtn) {
        const resetSubmitButton = () => {
            if (submitAdminBtn.disabled) {
                submitAdminBtn.disabled = false;
                submitAdminBtn.textContent = submitAdminBtn.dataset.originalText;
            }
        };

        submitAdminBtn.dataset.originalText = submitAdminBtn.textContent;

        adminPenggunaanForm.addEventListener("submit", function() {
            if (adminPenggunaanForm.checkValidity()) {
                submitAdminBtn.disabled = true;
                submitAdminBtn.textContent = "Sedang diproses...";
            }
        });

        window.addEventListener('pageshow', (event) => {
            if (event.persisted) {
                resetSubmitButton();
            }
        });

        const flashMessagesContainer = document.querySelector('.flash-messages-container');
        if (flashMessagesContainer && flashMessagesContainer.children.length > 0) {
            resetSubmitButton();
        }
    }

    // --- Chart.js for Pelanggan Dashboard ---
    console.log("Attempting to initialize Chart.js for monthly usage."); 

    const monthlyUsageChartCanvas = document.getElementById('monthlyUsageChart');
    console.log("Canvas element found:", monthlyUsageChartCanvas);

    if (monthlyUsageChartCanvas) {
        console.log("Canvas element exists. Proceeding with chart setup.");
        
        // Ambil data langsung dari variabel global yang didefinisikan di HTML
        const usageData = window.dataChartJs; 
        console.log("Data for chart (from window.dataChartJs):", usageData);

        if (usageData && usageData.length > 0) { // Pastikan data ada isinya
            try {
                // Konversi data ke format yang benar jika masih ada string di dalamnya
                const processedUsageData = usageData.map(item => ({
                    bulan: item.bulan,
                    tahun: item.tahun,
                    total_kwh_bulan: parseFloat(item.total_kwh_bulan),
                    total_tagihan_bulan: parseFloat(item.total_tagihan_bulan)
                }));

                // Sortir data agar urutan bulan/tahun benar
                processedUsageData.sort((a, b) => {
                    if (a.tahun === b.tahun) {
                        return a.bulan - b.bulan;
                    }
                    return a.tahun - b.tahun;
                });

                const labels = processedUsageData.map(item => `${item.bulan}/${item.tahun}`);
                const kwhData = processedUsageData.map(item => item.total_kwh_bulan);
                const billData = processedUsageData.map(item => item.total_tagihan_bulan); 

                const ctx = monthlyUsageChartCanvas.getContext('2d');
                console.log("Chart context obtained. Initializing Chart.js instance.");

                new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: labels,
                        datasets: [
                            {
                                label: 'Total KWH Terpakai',
                                data: kwhData,
                                backgroundColor: 'rgba(74, 144, 226, 0.7)',
                                borderColor: 'rgba(74, 144, 226, 1)',
                                borderWidth: 1,
                                yAxisID: 'y-kwh',
                                borderRadius: 5,
                            },
                            {
                                label: 'Total Tagihan (Rp)',
                                data: billData,
                                backgroundColor: 'rgba(255, 193, 7, 0.7)',
                                borderColor: 'rgba(255, 193, 7, 1)',
                                borderWidth: 1,
                                type: 'line',
                                fill: false,
                                yAxisID: 'y-bill',
                                tension: 0.3,
                                pointBackgroundColor: 'rgba(255, 193, 7, 1)',
                                pointBorderColor: '#fff',
                                pointBorderWidth: 2,
                                pointRadius: 5,
                                pointHoverRadius: 7,
                            }
                        ]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            title: {
                                display: true,
                                text: 'Riwayat Penggunaan dan Tagihan Bulanan',
                                font: {
                                    size: 16,
                                    weight: '600',
                                    family: 'Poppins'
                                },
                                color: '#333'
                            },
                            tooltip: {
                                mode: 'index',
                                intersect: false,
                                callbacks: {
                                    label: function(context) {
                                        let label = context.dataset.label || '';
                                        if (label) {
                                            label += ': ';
                                        }
                                        if (context.dataset.yAxisID === 'y-bill') {
                                            return label + 'Rp ' + parseFloat(context.raw).toLocaleString('id-ID', {minimumFractionDigits: 0, maximumFractionDigits: 2});
                                        }
                                        return label + context.raw + (context.dataset.yAxisID === 'y-kwh' ? ' kWh' : '');
                                    }
                                }
                            },
                            legend: {
                                labels: {
                                    font: {
                                        family: 'Poppins'
                                    }
                                }
                            }
                        },
                        scales: {
                            x: {
                                title: {
                                    display: true,
                                    text: 'Periode (Bulan/Tahun)',
                                    font: { family: 'Poppins' }
                                },
                                grid: {
                                    display: false
                                },
                                ticks: {
                                    font: { family: 'Poppins' }
                                }
                            },
                            'y-kwh': {
                                type: 'linear',
                                position: 'left',
                                title: {
                                    display: true,
                                    text: 'Penggunaan (kWh)',
                                    font: { family: 'Poppins' }
                                },
                                beginAtZero: true,
                                ticks: {
                                    callback: function(value) {
                                        return value + ' kWh';
                                    },
                                    font: { family: 'Poppins' }
                                },
                                grid: {
                                    color: 'rgba(0, 0, 0, 0.05)'
                                }
                            },
                            'y-bill': {
                                type: 'linear',
                                position: 'right',
                                title: {
                                    display: true,
                                    text: 'Total Tagihan (Rp)',
                                    font: { family: 'Poppins' }
                                },
                                beginAtZero: true,
                                grid: {
                                    drawOnChartArea: false
                                },
                                ticks: {
                                    callback: function(value) {
                                        return 'Rp ' + value.toLocaleString('id-ID', {minimumFractionDigits: 0, maximumFractionDigits: 2});
                                    },
                                    font: { family: 'Poppins' }
                                }
                            }
                        }
                    }
                });
                console.log("Chart.js initialization complete.");

            } catch (e) {
                console.error("Error during Chart.js setup or data parsing:", e);
                // Log the raw data if it was problematic
                console.error("Problematic data sent to chart:", usageData); 
            }
        } else {
            console.warn("No data available for chart. Chart will not be displayed.");
        }
    } else {
        console.warn("Canvas element with ID 'monthlyUsageChart' not found on this page. Chart will not be displayed.");
    }
});