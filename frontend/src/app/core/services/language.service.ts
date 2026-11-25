import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';

export type Language = 'en' | 'ar';

export interface Translations {
  [key: string]: {
    en: string;
    ar: string;
  };
}

export const AUTH_TRANSLATIONS: Translations = {
  // Brand Panel - Login
  loginBrandTitle1: { en: 'Welcome Back to', ar: 'أهلاً بك مجدداً في' },
  loginBrandTitle2: { en: 'Portal!', ar: 'بوابة' },
  jeebly: { en: 'Jeebly', ar: 'جيـبلي' },

  // Brand Panel - Register
  registerBrandTitle1: { en: 'Get Started with', ar: 'ابدأ رحلتك مع' },
  registerBrandTitle2: { en: 'Today!', ar: 'اليوم!' },

  // Form - Top Switch Bar
  dontHaveAccount: { en: "Don't have an account?", ar: 'ليس لديك حساب؟' },
  alreadyHaveAccount: { en: 'Already have an account?', ar: 'هل لديك حساب بالفعل؟' },
  signUpLink: { en: 'Sign Up', ar: 'إنشاء حساب' },
  signInLink: { en: 'Login', ar: 'تسجيل الدخول' },

  // Form - Headers
  welcomeBack: { en: 'Login', ar: 'تسجيل الدخول' },
  loginTitle: { en: 'Login', ar: 'تسجيل الدخول' },
  createAccount: { en: 'Create Your Account', ar: 'إنشاء حساب جديد' },

  // Form - Fields
  fullNameLabel: { en: 'Full Name', ar: 'الاسم الكامل' },
  fullNamePlaceholder: { en: 'Full Name', ar: 'الاسم الكامل' },
  emailLabel: { en: 'Email Address', ar: 'البريد الإلكتروني' },
  emailPlaceholder: { en: 'Email Address', ar: 'البريد الإلكتروني' },
  passwordLabel: { en: 'Password', ar: 'كلمة المرور' },
  passwordPlaceholder: { en: 'Password', ar: 'كلمة المرور' },
  phoneLabel: { en: 'Phone Number', ar: 'رقم الهاتف' },
  phonePlaceholder: { en: 'Phone Number', ar: 'رقم الهاتف' },
  confirmPasswordLabel: { en: 'Confirm Password', ar: 'تأكيد كلمة المرور' },
  reenterPasswordPlaceholder: { en: 'Re-enter password', ar: 'أعد إدخال كلمة المرور' },

  // Form - Options
  rememberMe: { en: 'Remember me', ar: 'تذكرني' },
  forgotPassword: { en: 'Forgot password?', ar: 'نسيت كلمة المرور؟' },

  // Buttons
  signInBtn: { en: 'Login', ar: 'تسجيل الدخول' },
  loginBtn: { en: 'Login', ar: 'تسجيل الدخول' },
  signingInBtn: { en: 'Logging in...', ar: 'جاري تسجيل الدخول...' },
  signUpBtn: { en: 'Sign Up', ar: 'إنشاء الحساب' },
  creatingAccountBtn: { en: 'Creating Account...', ar: 'جاري إنشاء الحساب...' },

  // Validation Messages
  fullNameRequired: { en: 'Full name is required.', ar: 'الاسم الكامل مطلوب.' },
  fullNameMinLength: { en: 'Full name must be at least 3 characters.', ar: 'يجب أن لا يقل الاسم عن 3 أحرف.' },
  emailRequired: { en: 'Email is required.', ar: 'البريد الإلكتروني مطلوب.' },
  emailInvalid: { en: 'Please enter a valid email address.', ar: 'يرجى إدخال بريد إلكتروني صالح.' },
  passwordRequired: { en: 'Password is required.', ar: 'كلمة المرور مطلوبة.' },
  passwordMinLength: { en: 'Password must be at least 6 characters.', ar: 'يجب أن لا تقل كلمة المرور عن 6 أحرف.' },

  // Language Switch
  langEnglish: { en: 'English', ar: 'English' },
  langArabic: { en: 'العربية', ar: 'العربية' },
  langArabicAE: { en: 'العربية AE', ar: 'العربية AE' },

  // Navigation / Main Menu
  mainMenu: { en: 'MAIN MENU', ar: 'القائمة الرئيسية' },
  dashboard: { en: 'Dashboard', ar: 'لوحة التحكم' },
  orders: { en: 'Orders', ar: 'الطلبات' },
  riders: { en: 'Riders', ar: 'السائقون' },
  myProfile: { en: 'My Profile', ar: 'ملفي الشخصي' },
  profileDetails: { en: 'View & edit profile details', ar: 'عرض وتعديل بيانات الحساب' },
  securityPassword: { en: 'Security & Password', ar: 'الأمان وكلمة المرور' },
  securitySubtitle: { en: 'Update your access credentials', ar: 'تحديث بيانات الدخول' },
  logout: { en: 'Sign Out', ar: 'تسجيل الخروج' },
  welcomeGreeting: { en: 'Welcome back,', ar: 'مرحباً بعودتك،' },

  // Orders Module
  ordersManagement: { en: 'Orders Management', ar: 'إدارة الطلبات' },
  ordersSubtitle: { en: 'Create, track, and dispatch delivery orders across the fleet', ar: 'إنشاء ومتابعة وتوزيع طلبات التوصيل عبر الأسطول' },
  filterSearchOrders: { en: 'Filter & Search Orders', ar: 'تصفية وبحث الطلبات' },
  filterSearchSubtitle: { en: 'Quickly locate specific orders by customer, status, rider, or date', ar: 'البحث السريع عن الطلبات حسب العميل، الحالة، السائق أو التاريخ' },
  searchQuery: { en: 'Search Query', ar: 'بحث' },
  searchPlaceholder: { en: 'Search by order ID, customer name...', ar: 'ابحث برقم الطلب، اسم العميل...' },
  orderStatus: { en: 'Order Status', ar: 'حالة الطلب' },
  allStatuses: { en: 'All Statuses', ar: 'جميع الحالات' },
  assignedRider: { en: 'Assigned Rider', ar: 'السائق المعين' },
  allRiders: { en: 'All Riders', ar: 'جميع السائقين' },
  createdFrom: { en: 'Created From', ar: 'تاريخ البدء' },
  createdTo: { en: 'Created To', ar: 'تاريخ الانتهاء' },
  sortOrder: { en: 'Sort Order', ar: 'الترتيب' },
  newestFirst: { en: 'Newest First', ar: 'الأحدث أولاً' },
  oldestFirst: { en: 'Oldest First', ar: 'الأقدم أولاً' },
  clearFilters: { en: 'Clear Filters', ar: 'إعادة ضبط التصفية' },
  createOrder: { en: 'Create Order', ar: 'إنشاء طلب' },
  download: { en: 'Download', ar: 'تحميل' },
  downloadExcel: { en: 'Download as Excel (.xlsx)', ar: 'تحميل كملف إكسل (.xlsx)' },
  downloadCsv: { en: 'Download as CSV (.csv)', ar: 'تحميل كملف CSV (.csv)' },
  deleteReport: { en: 'Delete Generated Report', ar: 'حذف التقرير المُنشأ' },
  rowsPerPage: { en: 'Rows per page:', ar: 'عدد الصفوف لكل صفحة:' },

  // Table Headers
  orderIdCol: { en: 'ORDER ID', ar: 'رقم الطلب' },
  customerCol: { en: 'CUSTOMER', ar: 'العميل' },
  pickupCol: { en: 'PICKUP', ar: 'مكان الاستلام' },
  deliveryCol: { en: 'DELIVERY', ar: 'مكان التسليم' },
  amountCol: { en: 'AMOUNT', ar: 'المبلغ' },
  riderCol: { en: 'RIDER', ar: 'السائق' },
  statusCol: { en: 'STATUS', ar: 'الحالة' },
  createdAtCol: { en: 'CREATED AT', ar: 'تاريخ الإنشاء' },
  assignRiderCol: { en: 'ASSIGN RIDER', ar: 'تعيين السائق' },
  actionsCol: { en: 'ACTIONS', ar: 'الإجراءات' },
  unassigned: { en: 'Unassigned', ar: 'غير معين' },

  // Order Status Values
  statusPending: { en: 'Pending', ar: 'قيد الانتظار' },
  statusAccepted: { en: 'Accepted', ar: 'تم القبول' },
  statusPickedUp: { en: 'Picked Up', ar: 'تم الاستلام' },
  statusOnTheWay: { en: 'On The Way', ar: 'في الطريق' },
  statusDelivered: { en: 'Delivered', ar: 'تم التوصيل' },
  statusCancelled: { en: 'Cancelled', ar: 'ملغي' },

  // Riders Module
  riderList: { en: 'Rider List', ar: 'قائمة السائقين' },
  totalRiders: { en: 'Total Riders', ar: 'إجمالي السائقين' },
  filterSearchRiders: { en: 'Filter & Search Riders', ar: 'تصفية وبحث السائقين' },
  filterRidersSubtitle: { en: 'Quickly locate specific riders by name, contact, status, or date', ar: 'البحث عن السائقين حسب الاسم، رقم التواصل، الحالة أو التاريخ' },
  addRider: { en: 'Add Rider', ar: 'إضافة سائق' },
  riderStatus: { en: 'Rider Status', ar: 'حالة السائق' },
  availability: { en: 'Availability', ar: 'التوفر' },
  vehicle: { en: 'Vehicle', ar: 'المركبة' },
  allAvailability: { en: 'All Availability', ar: 'جميع حالات التوفر' },
  active: { en: 'Active', ar: 'نشط' },
  inactive: { en: 'Inactive', ar: 'غير نشط' },
  available: { en: 'Available', ar: 'متاح' },
  busy: { en: 'Busy', ar: 'مشغول' },
  unavailable: { en: 'Unavailable', ar: 'غير متاح' },

  // Profile & Password
  accountProfile: { en: 'Account Profile', ar: 'الملف الشخصي' },
  profileSubtitle: { en: 'Manage your account credentials, contact information, and avatar photo', ar: 'إدارة بيانات الحساب ومعلومات التواصل والصورة الشخصية' },
  personalInfo: { en: 'Personal Information', ar: 'المعلومات الشخصية' },
  personalInfoSubtitle: { en: 'Update your display name and registered mobile contact number', ar: 'تحديث اسم العرض ورقم الهاتف المسجل' },
  mobileContactNumber: { en: 'Mobile Contact Number', ar: 'رقم الهاتف للتواصل' },
  saveProfileChanges: { en: 'Save Profile Changes', ar: 'حفظ التغييرات' },
  removePhoto: { en: 'Remove Photo', ar: 'حذف الصورة' },
  changePassword: { en: 'Change Password', ar: 'تغيير كلمة المرور' },
  currentPassword: { en: 'Current Password', ar: 'كلمة المرور الحالية' },
  newPassword: { en: 'New Password', ar: 'كلمة المرور الجديدة' },
  confirmNewPassword: { en: 'Confirm New Password', ar: 'تأكيد كلمة المرور الجديدة' },
  updatePassword: { en: 'Update Password', ar: 'تحديث كلمة المرور' },
  passwordHelperText: { en: 'Must be at least 8 characters long and different from your current password.', ar: 'يجب أن لا تقل عن 8 أحرف وتكون مختلفة عن كلمة المرور الحالية.' },

  // Common UI Actions
  cancel: { en: 'Cancel', ar: 'إلغاء' },
  save: { en: 'Save', ar: 'حفظ' },
  close: { en: 'Close', ar: 'إغلاق' },
  confirm: { en: 'Confirm', ar: 'تأكيد' },
  delete: { en: 'Delete', ar: 'حذف' },
  edit: { en: 'Edit', ar: 'تعديل' },
  view: { en: 'View', ar: 'عرض' }
};

export const PHRASE_DICTIONARY: Record<string, string> = {
  // Dashboard
  'analytic overview': 'نظرة تحليلية عامة',
  'real-time delivery performance and fleet operations summary': 'ملخص أداء التوصيل وعمليات الأسطول في الوقت الفعلي',
  'live fleet': 'الأسطول المباشر',
  'total orders': 'إجمالي الطلبات',
  'total orders recorded': 'إجمالي الطلبات المسجلة',
  'volume share': 'نسبة الحجم',
  'delivered orders': 'الطلبات المسلمة',
  'orders successfully delivered': 'طلبات تم تسليمها بنجاح',
  'delivery success rate': 'نسبة نجاح التوصيل',
  'in progress orders': 'طلبات قيد التنفيذ',
  'orders in active transit': 'طلبات جاري توصيلها حالياً',
  'active transit ratio': 'نسبة الطلبات قيد التوصيل',
  'cancelled orders': 'الطلبات الملغاة',
  'cancellation rate': 'نسبة الإلغاء',
  'rider summary': 'ملخص السائقين',
  'current status of delivery fleet personnel': 'الحالة الحالية لفرق التوصيل بالأسطول',
  'riders ready for assignment': 'سائقون جاهزون لتعيين الطلبات',
  'busy riders on active orders': 'سائقون مشغولون في توصيل الطلبات',
  'active fleet members': 'أعضاء الأسطول النشطون',
  'inactive riders': 'سائقون غير نشطين',
  'on order': 'في مهمة توصيل',
  'riders currently delivering': 'سائقون يقومون بالتوصيل حالياً',
  'scheduled break': 'استراحة مجدولة',
  'riders on official break': 'سائقون في استراحة رسمية',
  'on leave / absent': 'في إجازة / غائب',
  'absent': 'غائب',
  'riders on leave or off-duty': 'سائقون في إجازة أو خارج الخدمة',
  'comparative volume distribution': 'توزيع الحجم المقارن',
  'recent orders': 'أحدث الطلبات',
  'latest 5 dispatch operations': 'آخر 5 عمليات إرسال وتوصيل',
  'view all': 'عرض الكل',
  'available riders': 'السائقون المتاحون',
  'fleet ready for dispatch': 'أسطول جاهز للإرسال',
  'available for dispatch': 'متاح للإرسال',
  'no recent orders found': 'لا توجد طلبات حديثة',
  'no riders currently available': 'لا يوجد سائقون متاحون حالياً',
  'no orders recorded yet.': 'لا توجد طلبات مسجلة بعد.',
  'loading dashboard updates...': 'جاري تحميل تحديثات لوحة التحكم...',
  'order records': 'سجلات الطلبات',
  'downloading...': 'جاري التحميل...',
  'download': 'تحميل',
  'download as excel (.xlsx)': 'تحميل كملف إكسل (.xlsx)',
  'download as csv (.csv)': 'تحميل كملف CSV (.csv)',
  'delete generated report': 'حذف التقرير المُنشأ',
  'create order': 'إنشاء طلب',
  'order lifecycle & details': 'تفاصيل ومراحل الطلب',
  'order lifecycle journey': 'مسار ومراحل دورة حياة الطلب',
  'order placed': 'تم تقديم الطلب',
  'order registered in jeebly dispatch system.': 'تم تسجيل الطلب في نظام إرسال جيـبلي.',
  'rider assigned': 'تم تعيين السائق',
  'order assigned to fleet rider for fulfillment.': 'تم إسناد الطلب إلى سائق الأسطول للتنفيذ.',
  'order picked up': 'تم استلام الطلب',
  'rider picked up package from origin location.': 'استلم السائق الطرد من موقع الانطلاق.',
  'delivered to destination': 'تم التسليم إلى الوجهة',
  'package successfully handed over to customer.': 'تم تسليم الطرد بنجاح إلى العميل.',
  'delivery cancelled': 'تم إلغاء التوصيل',
  'order was cancelled prior to final delivery.': 'تم إلغاء الطلب قبل إتمام التوصيل النهائي.',
  'customer information': 'معلومات العميل',
  'customer name': 'اسم العميل',
  'mobile number': 'رقم الهاتف المتحرك',
  'phone number': 'رقم الهاتف',
  'delivery routing': 'مسار التوصيل',
  'pickup address': 'عنوان الاستلام',
  'pickup address (places autocomplete)': 'عنوان الاستلام',
  'delivery destination (places autocomplete)': 'وجهة التسليم',
  'delivery destination': 'وجهة التسليم',
  'item / amount': 'الصنف / المبلغ',
  'order item': 'صنف الطلب',
  'enter item name': 'أدخل اسم الصنف',
  'order details': 'تفاصيل الطلب',
  'customer details': 'بيانات العميل',
  'delivery route': 'مسار التوصيل',
  'enter amount': 'أدخل المبلغ',
  '10-digit mobile number': 'رقم الهاتف (10 أرقام)',
  'enter customer name': 'أدخل اسم العميل',
  'delivery address': 'عنوان التسليم',
  'fleet assignment': 'تعيين الأسطول',
  'assigned fleet rider': 'سائق الأسطول المعين',
  'financial summary': 'الملخص المالي',
  'order value': 'قيمة الطلب',
  'total amount': 'المبلغ الإجمالي',
  'order value / amount': 'قيمة / مبلغ الطلب',
  'edit order details': 'تعديل بيانات الطلب',
  'create new delivery order': 'إنشاء طلب توصيل جديد',
  'update shipment details, location coordinates, or pricing.': 'تحديث بيانات الشحنة، إحداثيات الموقع، أو الأسعار.',
  'fill in the customer information and delivery coordinates.': 'أدخل معلومات العميل وإحداثيات التسليم.',
  'enter full customer name': 'أدخل الاسم الكامل للعميل',
  'enter pickup location or address': 'أدخل موقع أو عنوان الاستلام',
  'enter delivery destination or landmark': 'أدخل وجهة أو معلم التسليم',
  'enter a valid non-negative amount.': 'أدخل مبلغاً صالحاً غير سالب.',
  'customer name is required (maximum 100 characters).': 'اسم العميل مطلوب (100 حرف كحد أقصى).',
  'customer name is required.': 'اسم العميل مطلوب.',
  'confirm order deletion': 'تأكيد حذف الطلب',
  'are you sure you want to delete order': 'هل أنت متأكد من رغبتك في حذف الطلب',
  'this action cannot be undone. all associated lifecycle records will be permanently removed.': 'لا يمكن التراجع عن هذا الإجراء. سيتم حذف جميع السجلات المرتبطة نهائياً.',
  'this action cannot be undone.': 'لا يمكن التراجع عن هذا الإجراء.',
  'deleting...': 'جاري الحذف...',
  'loading orders list...': 'جاري تحميل قائمة الطلبات...',
  'no orders match your search criteria.': 'لا توجد طلبات تطابق معايير البحث.',
  'previous': 'السابق',
  'next': 'التالي',
  'rider profile & details': 'ملف وتفاصيل السائق',
  'operational information': 'المعلومات التشغيلية',
  'joining date': 'تاريخ الانضمام',
  'performance & orders': 'الأداء والطلبات',
  'total deliveries': 'إجمالي عمليات التسليم',
  'active assignments': 'المهام النشطة',
  'upload rider photo': 'رفع صورة السائق',
  'change photo': 'تغيير الصورة',
  'confirm rider deletion': 'تأكيد حذف السائق',
  'are you sure you want to remove rider': 'هل أنت متأكد من إزالة السائق',
  'all active delivery assignments will be unlinked.': 'سيتم فك ارتباط جميع مهام التوصيل النشطة.',
  'create rider': 'إنشاء سائق',
  'update rider': 'تحديث السائق',
  'enter rider name': 'أدخل اسم السائق',
  'enter mobile number': 'أدخل رقم الهاتف',
  'enter email': 'أدخل البريد الإلكتروني',
  'enter new rider information': 'أدخل معلومات السائق الجديد',
  'update rider information': 'تحديث معلومات السائق',
  'back to riders': 'العودة إلى السائقين',
  'loading rider details...': 'جاري تحميل تفاصيل السائق...',
  'loading riders…': 'جاري تحميل السائقين…',
  'loading riders...': 'جاري تحميل السائقين...',
  'ascending (a-z, 1-9)': 'تصاعدي (أ-ي، 1-9)',
  'descending (z-a, 9-1)': 'تنازلي (ي-أ، 9-1)',
  'search by name, mobile, email...': 'ابحث بالاسم، الهاتف، البريد...',
  'all vehicles': 'جميع المركبات',
  'bike': 'دراجة',
  'scooter': 'سكوتر',
  'car': 'سيارة',
  'van': 'شاحنة صغيرة',
  'motorcycle': 'دراجة نارية',
  'delivered': 'تم التوصيل',
  'in progress': 'قيد التنفيذ',
  'cancelled': 'ملغي',
  'pending': 'قيد الانتظار',
  'accepted': 'تم القبول',
  'preparing': 'قيد التحضير',
  'ready': 'جاهز للتوصيل',
  'out for delivery': 'خرج للتوصيل',
  'out_for_delivery': 'خرج للتوصيل',
  'picked up': 'تم الاستلام',
  'on the way': 'في الطريق',
  'active': 'نشط',
  'inactive': 'غير نشط',
  'available': 'متاح',
  'busy': 'مشغول',
  'unavailable': 'غير متاح',
  'save profile changes': 'حفظ التغييرات',
  'saving changes...': 'جاري حفظ التغييرات...',
  'remove photo': 'حذف الصورة',
  'upload profile photo': 'رفع صورة شخصية',
  'loading profile information...': 'جاري تحميل بيانات الملف الشخصي...',
  'jeebly administrator': 'مسؤول جيـبلي',
  'profile updated successfully!': 'تم تحديث الملف الشخصي بنجاح!',
  'enter your current password': 'أدخل كلمة المرور الحالية',
  'create a strong password (min. 8 characters)': 'أنشئ كلمة مرور قوية (8 أحرف كحد أدنى)',
  're-enter your new password to confirm': 'أعد إدخال كلمة المرور الجديدة للتأكيد',
  'updating password...': 'جاري تحديث كلمة المرور...',
  'current password is required.': 'كلمة المرور الحالية مطلوبة.',
  'new password is required.': 'كلمة المرور الجديدة مطلوبة.',
  'confirm password is required.': 'تأكيد كلمة المرور مطلوب.',
  'passwords do not match.': 'كلمتا المرور غير متطابقتين.',
  'password updated successfully.': 'تم تحديث كلمة المرور بنجاح.',
  'hide password': 'إخفاء كلمة المرور',
  'show password': 'إظهار كلمة المرور',
  'home': 'الرئيسية',
  'collapse menu': 'طي القائمة',
  'expand sidebar': 'توسيع الشريط الجانبي',
  'collapse sidebar': 'طي الشريط الجانبي',
  'log out of jeebly portal': 'تسجيل الخروج من بوابة جيـبلي',
  'change to arabic': 'تغيير إلى العربية',
  'change to english': 'تغيير إلى الإنجليزية'
};

@Injectable({
  providedIn: 'root'
})
export class LanguageService {
  private currentLangSubject = new BehaviorSubject<Language>(this.getInitialLanguage());
  public currentLang$: Observable<Language> = this.currentLangSubject.asObservable();
  private enToArMap = new Map<string, string>();

  constructor() {
    this.buildTranslationCache();
    this.applyLanguage(this.currentLangSubject.value);
  }

  private buildTranslationCache(): void {
    // 1. Index AUTH_TRANSLATIONS
    for (const key of Object.keys(AUTH_TRANSLATIONS)) {
      const entry = AUTH_TRANSLATIONS[key];
      if (entry) {
        this.enToArMap.set(key.toLowerCase(), entry.ar);
        this.enToArMap.set(entry.en.toLowerCase().trim(), entry.ar);
      }
    }

    // 2. Index PHRASE_DICTIONARY
    for (const [enPhrase, arPhrase] of Object.entries(PHRASE_DICTIONARY)) {
      this.enToArMap.set(enPhrase.toLowerCase().trim(), arPhrase);
    }
  }

  public get currentLang(): Language {
    return this.currentLangSubject.value;
  }

  public get isArabic(): boolean {
    return this.currentLang === 'ar';
  }

  public setLanguage(lang: Language): void {
    if (lang !== this.currentLang) {
      this.currentLangSubject.next(lang);
      try {
        localStorage.setItem('jeebly_lang', lang);
      } catch (e) {
        // Safe fallback if storage unavailable
      }
      this.applyLanguage(lang);
    }
  }

  public toggleLanguage(): void {
    this.setLanguage(this.isArabic ? 'en' : 'ar');
  }

  public t(keyOrText: string): string {
    if (!keyOrText) return '';

    // If English is active:
    if (!this.isArabic) {
      const entry = AUTH_TRANSLATIONS[keyOrText] || AUTH_TRANSLATIONS[keyOrText.trim()];
      if (entry) return entry.en;
      return keyOrText;
    }

    // If Arabic is active:
    const trimmed = keyOrText.trim();

    // 1. Exact key in AUTH_TRANSLATIONS
    if (AUTH_TRANSLATIONS[keyOrText]?.ar) {
      return AUTH_TRANSLATIONS[keyOrText].ar;
    }
    if (AUTH_TRANSLATIONS[trimmed]?.ar) {
      return AUTH_TRANSLATIONS[trimmed].ar;
    }

    // 2. Lookup in normalized map (case-insensitive)
    const lower = trimmed.toLowerCase();
    const mapped = this.enToArMap.get(lower);
    if (mapped) {
      return mapped;
    }

    return keyOrText;
  }

  private getInitialLanguage(): Language {
    try {
      const saved = localStorage.getItem('jeebly_lang') as Language;
      if (saved === 'ar' || saved === 'en') {
        return saved;
      }
    } catch (e) {
      // Safe fallback
    }
    return 'en';
  }

  private applyLanguage(lang: Language): void {
    if (typeof document !== 'undefined') {
      const isRtl = lang === 'ar';
      document.documentElement.setAttribute('dir', isRtl ? 'rtl' : 'ltr');
      document.documentElement.setAttribute('lang', lang);
      if (isRtl) {
        document.body.classList.add('rtl-mode');
      } else {
        document.body.classList.remove('rtl-mode');
      }
    }
  }
}
