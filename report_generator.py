from datetime import datetime
import pandas as pd

class PatientReportGenerator:
    """مولد تقارير المرضى"""
    
    @staticmethod
    def generate_html_report(patient_data, appointments_data, payments_data, treatments_data):
        """توليد تقرير HTML شامل للمريض"""
        
        # حساب الإحصائيات
        total_visits = len(appointments_data)
        completed_visits = len(appointments_data[appointments_data['status'] == 'مكتمل']) if not appointments_data.empty else 0
        total_spent = appointments_data['total_cost'].sum() if not appointments_data.empty else 0
        total_paid = payments_data['amount'].sum() if not payments_data.empty else 0
        total_pending = total_spent - total_paid
        
        # معلومات المريض
        patient_info = f"""
        <div class='patient-report'>
            <div class='report-header'>
                <h2>📋 تقرير شامل للمريض</h2>
                <h3>{patient_data['name']}</h3>
                <p>تاريخ التقرير: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
            </div>
            
            <div class='report-section'>
                <h3>👤 المعلومات الشخصية</h3>
                <table class='report-table'>
                    <tr><th>الاسم</th><td>{patient_data['name']}</td></tr>
                    <tr><th>رقم الهاتف</th><td>{patient_data['phone']}</td></tr>
                    <tr><th>البريد الإلكتروني</th><td>{patient_data.get('email', 'غير محدد')}</td></tr>
                    <tr><th>العنوان</th><td>{patient_data.get('address', 'غير محدد')}</td></tr>
                    <tr><th>تاريخ الميلاد</th><td>{patient_data.get('date_of_birth', 'غير محدد')}</td></tr>
                    <tr><th>النوع</th><td>{patient_data.get('gender', 'غير محدد')}</td></tr>
                    <tr><th>فصيلة الدم</th><td>{patient_data.get('blood_type', 'غير محدد')}</td></tr>
                    <tr><th>الحساسية</th><td>{patient_data.get('allergies', 'لا يوجد')}</td></tr>
                    <tr><th>جهة الاتصال للطوارئ</th><td>{patient_data.get('emergency_contact', 'غير محدد')}</td></tr>
                </table>
            </div>
            
            <div class='report-section'>
                <h3>📊 الإحصائيات العامة</h3>
                <table class='report-table'>
                    <tr><th>إجمالي الزيارات</th><td>{total_visits} زيارة</td></tr>
                    <tr><th>الزيارات المكتملة</th><td>{completed_visits} زيارة</td></tr>
                    <tr><th>إجمالي التكاليف</th><td>{total_spent:,.2f} ج.م</td></tr>
                    <tr><th>المبلغ المدفوع</th><td>{total_paid:,.2f} ج.م</td></tr>
                    <tr><th>المبلغ المتبقي</th><td style='color: {"red" if total_pending > 0 else "green"};'>{total_pending:,.2f} ج.م</td></tr>
                </table>
            </div>
        """
        
        # التاريخ الطبي
        if patient_data.get('medical_history'):
            patient_info += f"""
            <div class='report-section'>
                <h3>📝 التاريخ الطبي</h3>
                <p>{patient_data['medical_history']}</p>
            </div>
            """
        
        # ملاحظات إضافية
        if patient_data.get('notes'):
            patient_info += f"""
            <div class='report-section'>
                <h3>📌 ملاحظات</h3>
                <p>{patient_data['notes']}</p>
            </div>
            """
        
        # سجل المواعيد
        if not appointments_data.empty:
            appointments_html = """
            <div class='report-section'>
                <h3>📅 سجل المواعيد</h3>
                <table class='report-table'>
                    <thead>
                        <tr>
                            <th>التاريخ</th>
                            <th>الوقت</th>
                            <th>الطبيب</th>
                            <th>العلاج</th>
                            <th>الحالة</th>
                            <th>التكلفة</th>
                        </tr>
                    </thead>
                    <tbody>
            """
            
            for _, apt in appointments_data.iterrows():
                appointments_html += f"""
                    <tr>
                        <td>{apt['appointment_date']}</td>
                        <td>{apt['appointment_time']}</td>
                        <td>{apt['doctor_name']}</td>
                        <td>{apt['treatment_name']}</td>
                        <td>{apt['status']}</td>
                        <td>{apt['total_cost']:,.2f} ج.م</td>
                    </tr>
                """
            
            appointments_html += """
                    </tbody>
                </table>
            </div>
            """
            patient_info += appointments_html
        
        # سجل المدفوعات
        if not payments_data.empty:
            payments_html = """
            <div class='report-section'>
                <h3>💰 سجل المدفوعات</h3>
                <table class='report-table'>
                    <thead>
                        <tr>
                            <th>التاريخ</th>
                            <th>المبلغ</th>
                            <th>طريقة الدفع</th>
                            <th>الحالة</th>
                            <th>ملاحظات</th>
                        </tr>
                    </thead>
                    <tbody>
            """
            
            for _, pay in payments_data.iterrows():
                payments_html += f"""
                    <tr>
                        <td>{pay['payment_date']}</td>
                        <td>{pay['amount']:,.2f} ج.م</td>
                        <td>{pay['payment_method']}</td>
                        <td>{pay['status']}</td>
                        <td>{pay.get('notes', '')}</td>
                    </tr>
                """
            
            payments_html += """
                    </tbody>
                </table>
            </div>
            """
            patient_info += payments_html
        
        # العلاجات المستخدمة
        if not treatments_data.empty:
            treatments_summary = treatments_data.groupby('treatment_name').size().reset_index(name='count')
            treatments_summary.columns = ['العلاج', 'عدد المرات']
            
            treatments_html = """
            <div class='report-section'>
                <h3>💉 ملخص العلاجات</h3>
                <table class='report-table'>
                    <thead>
                        <tr>
                            <th>العلاج</th>
                            <th>عدد المرات</th>
                        </tr>
                    </thead>
                    <tbody>
            """
            
            for _, treat in treatments_summary.iterrows():
                treatments_html += f"""
                    <tr>
                        <td>{treat['العلاج']}</td>
                        <td>{treat['عدد المرات']}</td>
                    </tr>
                """
            
            treatments_html += """
                    </tbody>
                </table>
            </div>
            """
            patient_info += treatments_html
        
        patient_info += "</div>"
        
        return patient_info
