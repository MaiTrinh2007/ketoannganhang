import streamlit as st
from datetime import date, timedelta
import calendar


# ============================================================
# CẤU HÌNH TRANG
# ============================================================

st.set_page_config(
    page_title="Tính lãi tiền gửi tiết kiệm",
    page_icon="💰",
    layout="wide"
)

st.title("💰 ỨNG DỤNG TÍNH LÃI TIỀN GỬI TIẾT KIỆM")
st.write(
    "Tính tiền lãi theo số tiền gửi, kỳ hạn, lãi suất, "
    "hình thức nhận lãi và ngày gửi/rút."
)

st.divider()


# ============================================================
# HÀM HỖ TRỢ
# ============================================================

def add_months(input_date, months):
    """
    Cộng số tháng vào một ngày.
    Ví dụ:
    31/01 + 1 tháng -> 28/02 hoặc 29/02
    """

    month = input_date.month - 1 + months
    year = input_date.year + month // 12
    month = month % 12 + 1

    day = min(
        input_date.day,
        calendar.monthrange(year, month)[1]
    )

    return date(year, month, day)


def get_month_ranges(start_date, end_date):
    """
    Chia khoảng thời gian từ ngày gửi đến trước ngày rút
    thành từng tháng để tính và hiển thị lãi.
    """

    ranges = []

    current = start_date

    while current < end_date:

        # Ngày cuối tháng hiện tại
        last_day = calendar.monthrange(
            current.year,
            current.month
        )[1]

        month_end = date(
            current.year,
            current.month,
            last_day
        )

        # Khoảng hiện tại kết thúc trước ngày rút
        period_end = min(
            month_end + timedelta(days=1),
            end_date
        )

        # Số ngày được tính lãi
        days = (period_end - current).days

        if days > 0:
            ranges.append(
                {
                    "start": current,
                    "end": period_end - timedelta(days=1),
                    "days": days
                }
            )

        current = period_end

    return ranges


def format_money(value):
    """Định dạng tiền Việt Nam."""
    return f"{value:,.0f} VNĐ".replace(",", ".")


# ============================================================
# NHẬP THÔNG TIN
# ============================================================

st.subheader("📋 Thông tin tiền gửi")

col1, col2 = st.columns(2)

with col1:

    principal = st.number_input(
        "💵 Số tiền gửi (VNĐ)",
        min_value=0.0,
        value=10_000_000.0,
        step=1_000_000.0,
        format="%.0f"
    )

    term_months = st.selectbox(
        "📅 Kỳ hạn",
        options=[1, 2, 3, 6, 9, 12, 18, 24, 36],
        format_func=lambda x: f"{x} tháng"
    )

    annual_rate = st.number_input(
        "📈 Lãi suất theo năm (%)",
        min_value=0.0,
        value=5.0,
        step=0.1,
        format="%.2f"
    )


with col2:

    interest_payment = st.selectbox(
        "💳 Hình thức nhận lãi",
        [
            "Cuối kỳ",
            "Hàng tháng",
            "Đầu kỳ"
        ]
    )

    # --------------------------------------------------------
    # Lãi đơn / lãi kép
    # --------------------------------------------------------

    if interest_payment == "Cuối kỳ":

        interest_type = st.radio(
            "🧮 Phương pháp tính lãi",
            [
                "Lãi đơn",
                "Lãi kép"
            ],
            horizontal=True
        )

    else:

        interest_type = "Lãi đơn"

        st.info(
            "ℹ️ Lãi kép chỉ áp dụng cho hình thức "
            "**nhận lãi cuối kỳ**. "
            "Với hình thức này, hệ thống tự động sử dụng lãi đơn."
        )


# ============================================================
# NGÀY GỬI / NGÀY RÚT
# ============================================================

st.subheader("📆 Thời gian gửi tiền")

col3, col4 = st.columns(2)

with col3:

    deposit_date = st.date_input(
        "Ngày khách hàng gửi tiền",
        value=date.today()
    )

with col4:

    withdrawal_date = st.date_input(
        "Ngày khách hàng rút tiền",
        value=add_months(date.today(), term_months)
    )


# ============================================================
# TÍNH NGÀY ĐÁO HẠN
# ============================================================

maturity_date = add_months(
    deposit_date,
    term_months
)


# ============================================================
# KIỂM TRA DỮ LIỆU
# ============================================================

if withdrawal_date <= deposit_date:

    st.error(
        "❌ Ngày rút tiền phải sau ngày gửi tiền."
    )

    st.stop()


# ============================================================
# TÍNH SỐ NGÀY THỰC GỬI
# ============================================================

# Ví dụ:
# Gửi 01/01, rút 02/01
# => tính lãi ngày 01/01
# => số ngày = 1

actual_days = (withdrawal_date - deposit_date).days


# ============================================================
# KIỂM TRA ĐÁO HẠN
# ============================================================

if withdrawal_date < maturity_date:

    st.warning(
        f"⚠️ Khách hàng rút trước hạn. "
        f"Ngày đáo hạn theo kỳ hạn {term_months} tháng là "
        f"**{maturity_date.strftime('%d/%m/%Y')}**."
    )

elif withdrawal_date == maturity_date:

    st.success(
        "✅ Khách hàng rút đúng ngày đáo hạn."
    )

else:

    st.info(
        f"ℹ️ Khách hàng rút sau ngày đáo hạn "
        f"({maturity_date.strftime('%d/%m/%Y')}). "
        f"Hệ thống vẫn tính theo lãi suất đã nhập cho toàn bộ "
        f"thời gian thực gửi."
    )


# ============================================================
# THÔNG TIN TỔNG QUAN
# ============================================================

st.divider()

info1, info2, info3, info4 = st.columns(4)

with info1:
    st.metric(
        "Số tiền gửi",
        format_money(principal)
    )

with info2:
    st.metric(
        "Lãi suất",
        f"{annual_rate:.2f}%/năm"
    )

with info3:
    st.metric(
        "Thời gian thực gửi",
        f"{actual_days} ngày"
    )

with info4:
    st.metric(
        "Ngày đáo hạn",
        maturity_date.strftime("%d/%m/%Y")
    )


# ============================================================
# TÍNH LÃI
# ============================================================

if st.button(
    "🧮 TÍNH TIỀN LÃI",
    type="primary",
    use_container_width=True
):

    rate = annual_rate / 100
    daily_rate = rate / 365

    # --------------------------------------------------------
    # LÃI ĐƠN
    # --------------------------------------------------------

    if interest_type == "Lãi đơn":

        # Lãi đơn:
        # Lãi = Gốc × Lãi suất năm × Số ngày / 365

        total_interest = (
            principal
            * rate
            * actual_days
            / 365
        )

        # ----------------------------------------------------
        # LÃI HÀNG THÁNG
        # ----------------------------------------------------

        monthly_data = []

        month_ranges = get_month_ranges(
            deposit_date,
            withdrawal_date
        )

        for item in month_ranges:

            monthly_interest = (
                principal
                * rate
                * item["days"]
                / 365
            )

            monthly_data.append(
                {
                    "Tháng": item["start"].strftime("%m/%Y"),
                    "Từ ngày": item["start"].strftime("%d/%m/%Y"),
                    "Đến ngày": item["end"].strftime("%d/%m/%Y"),
                    "Số ngày": item["days"],
                    "Tiền lãi": monthly_interest
                }
            )


        # ----------------------------------------------------
        # HÌNH THỨC NHẬN LÃI
        # ----------------------------------------------------

        if interest_payment == "Cuối kỳ":

            interest_received_at_withdrawal = total_interest

            total_received = (
                principal
                + total_interest
            )

            interest_note = (
                "Toàn bộ tiền lãi được trả vào ngày rút tiền."
            )

        elif interest_payment == "Hàng tháng":

            # Lãi của các tháng hoàn chỉnh được nhận từng tháng.
            # Nếu tháng cuối chưa đủ tháng thì phần lãi còn lại
            # được nhận khi rút tiền.

            interest_received_at_withdrawal = 0

            full_months = 0

            for item in monthly_data:

                if item["Số ngày"] >= 28:
                    full_months += 1

            # Tính tổng lãi của tháng cuối chưa thanh toán
            # bằng cách xác định ngày nhận lãi theo ngày gửi.

            monthly_anniversary = deposit_date
            paid_interest = 0

            while True:

                next_anniversary = add_months(
                    deposit_date,
                    full_months + 1
                )

                if next_anniversary <= withdrawal_date:

                    full_months += 1

                else:

                    break

            # Tổng lãi đã được trả trước ngày rút
            for i in range(1, full_months + 1):

                anniversary_start = add_months(
                    deposit_date,
                    i - 1
                )

                anniversary_end = add_months(
                    deposit_date,
                    i
                )

                if anniversary_end <= withdrawal_date:

                    days_period = (
                        anniversary_end
                        - anniversary_start
                    ).days

                    paid_interest += (
                        principal
                        * rate
                        * days_period
                        / 365
                    )

            interest_received_at_withdrawal = (
                total_interest - paid_interest
            )

            total_received = (
                principal
                + interest_received_at_withdrawal
            )

            interest_note = (
                "Lãi của các kỳ tháng đã được trả hàng tháng. "
                "Ngày rút tiền chỉ nhận gốc và phần lãi còn lại "
                "của kỳ chưa đủ tháng."
            )

        else:
            # Đầu kỳ:
            # Lãi được trả ngay khi gửi tiền.
            interest_received_at_withdrawal = 0

            total_received = principal

            interest_note = (
                "Tiền lãi được trả cho khách hàng ngay tại thời điểm "
                "gửi tiền. Khi rút tiền, khách hàng nhận lại tiền gốc."
            )


    # ========================================================
    # LÃI KÉP
    # ========================================================

    else:

        # Lãi kép:
        #
        # A = P × (1 + r/365)^n
        #
        # Trong đó:
        # P = tiền gốc
        # r = lãi suất năm
        # n = số ngày thực gửi

        total_received = (
            principal
            * ((1 + rate / 365) ** actual_days)
        )

        total_interest = (
            total_received
            - principal
        )

        interest_received_at_withdrawal = (
            total_interest
        )

        interest_note = (
            "Lãi kép được áp dụng theo phương pháp "
            "tái nhập lãi hàng ngày và toàn bộ gốc + lãi "
            "được thanh toán vào ngày rút tiền."
        )

        # ----------------------------------------------------
        # BẢNG LÃI HÀNG THÁNG
        # ----------------------------------------------------

        monthly_data = []

        month_ranges = get_month_ranges(
            deposit_date,
            withdrawal_date
        )

        current_balance = principal

        for item in month_ranges:

            balance_before = current_balance

            monthly_balance = (
                current_balance
                * ((1 + rate / 365) ** item["days"])
            )

            monthly_interest = (
                monthly_balance
                - current_balance
            )

            current_balance = monthly_balance

            monthly_data.append(
                {
                    "Tháng": item["start"].strftime("%m/%Y"),
                    "Từ ngày": item["start"].strftime("%d/%m/%Y"),
                    "Đến ngày": item["end"].strftime("%d/%m/%Y"),
                    "Số ngày": item["days"],
                    "Tiền gốc đầu kỳ": balance_before,
                    "Tiền lãi": monthly_interest,
                    "Số dư cuối kỳ": current_balance
                }
            )


    # ========================================================
    # KẾT QUẢ
    # ========================================================

    st.divider()

    st.subheader("💰 KẾT QUẢ TÍNH TOÁN")

    result1, result2, result3 = st.columns(3)

    with result1:

        st.metric(
            "💵 Tổng tiền gốc",
            format_money(principal)
        )

    with result2:

        st.metric(
            "📈 Tổng tiền lãi",
            format_money(total_interest)
        )

    with result3:

        st.metric(
            "💰 Tổng tiền nhận",
            format_money(total_received)
        )


    # ========================================================
    # CHI TIẾT
    # ========================================================

    st.subheader("📊 Chi tiết tiền lãi")

    st.info(interest_note)


    # ========================================================
    # BẢNG LÃI THEO THÁNG
    # ========================================================

    if interest_type == "Lãi kép":

        st.write("### Lãi phát sinh theo từng tháng")

        display_data = []

        for row in monthly_data:

            display_data.append(
                {
                    "Tháng": row["Tháng"],
                    "Từ ngày": row["Từ ngày"],
                    "Đến ngày": row["Đến ngày"],
                    "Số ngày": row["Số ngày"],
                    "Gốc đầu kỳ": format_money(
                        row["Tiền gốc đầu kỳ"]
                    ),
                    "Tiền lãi": format_money(
                        row["Tiền lãi"]
                    ),
                    "Số dư cuối kỳ": format_money(
                        row["Số dư cuối kỳ"]
                    )
                }
            )

        st.dataframe(
            display_data,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.write("### Lãi theo từng tháng")

        display_data = []

        for row in monthly_data:

            display_data.append(
                {
                    "Tháng": row["Tháng"],
                    "Từ ngày": row["Từ ngày"],
                    "Đến ngày": row["Đến ngày"],
                    "Số ngày": row["Số ngày"],
                    "Tiền lãi": format_money(
                        row["Tiền lãi"]
                    )
                }
            )

        st.dataframe(
            display_data,
            use_container_width=True,
            hide_index=True
        )


    # ========================================================
    # THÔNG TIN NHẬN TIỀN NGÀY RÚT
    # ========================================================

    st.subheader("🏦 Số tiền khách hàng nhận vào ngày rút")

    withdrawal_col1, withdrawal_col2 = st.columns(2)

    with withdrawal_col1:

        st.write("**Tiền gốc:**")
        st.success(
            format_money(principal)
        )

    with withdrawal_col2:

        st.write("**Tiền lãi nhận tại ngày rút:**")
        st.success(
            format_money(
                interest_received_at_withdrawal
            )
        )


    st.markdown("---")

    st.markdown(
        f"""
        ### 💵 Tổng số tiền khách hàng nhận

        **{format_money(total_received)}**

        📅 Ngày gửi: **{deposit_date.strftime("%d/%m/%Y")}**

        📅 Ngày rút: **{withdrawal_date.strftime("%d/%m/%Y")}**

        ⏱️ Số ngày tính lãi: **{actual_days} ngày**

        📈 Lãi suất: **{annual_rate:.2f}%/năm**

        🧮 Phương pháp: **{interest_type}**

        💳 Hình thức nhận lãi: **{interest_payment}**
        """
    )


# ============================================================
# GHI CHÚ
# ============================================================

with st.expander("ℹ️ Quy ước tính lãi của ứng dụng"):

    st.markdown(
        """
        **1. Số ngày tính lãi**

        Ứng dụng tính từ **ngày gửi tiền đến trước ngày rút tiền**.

        Ví dụ:

        - Gửi ngày 01/10
        - Rút ngày 02/10
        - Số ngày tính lãi = **1 ngày**
        - Ngày 01/10 được tính lãi.
        - Ngày 02/10 không tính lãi.

        **2. Lãi đơn**

        Tiền lãi được tính theo:

        `Tiền lãi = Tiền gốc × Lãi suất năm × Số ngày / 365`

        **3. Lãi kép**

        Chỉ áp dụng khi chọn **nhận lãi cuối kỳ**.

        Lãi được tái nhập vào vốn và tính lãi kép theo ngày.

        **4. Nhận lãi hàng tháng**

        Tiền lãi phát sinh được chia theo từng khoảng thời gian
        và thể hiện trong bảng chi tiết.

        **5. Nhận lãi đầu kỳ**

        Tiền lãi được xem là đã trả cho khách hàng ngay khi gửi.
        Vì vậy khi đến ngày rút, khách hàng nhận lại tiền gốc.

        **6. Lưu ý**

        Ứng dụng đang tính theo **lãi suất người dùng nhập vào**
        cho toàn bộ thời gian thực gửi. Chưa áp dụng quy định
        riêng của từng ngân hàng về **lãi suất rút trước hạn,
        tất toán trước hạn hoặc điều chỉnh lãi suất**.
        """
    )
