from django.db import models

# User Profile
class Profile(models.Model):
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    full_name = models.CharField(max_length=200, blank=True)
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.username




    

# Tutor Profile
class Tutor(models.Model):
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    full_name = models.CharField(max_length=200, blank=True)
    expertise = models.TextField(blank=True)
    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Tutor: {self.full_name or self.username}"


    

# Skill
class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name



    

# User Skills
class ProfileSkill(models.Model):
    SKILL_TYPE = (
        ('teach', 'I Can Teach'),
        ('learn', 'I Want to Learn'),
    )
    
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='profile_skills')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    skill_type = models.CharField(max_length=10, choices=SKILL_TYPE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('profile', 'skill', 'skill_type')
    
    def __str__(self):
        return f"{self.profile.username} - {self.skill.name}"


    

# Skill Swap Request
class SkillSwapRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    )
    
    from_user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='sent_requests')
    to_user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='received_requests')
    skill_to_learn = models.ForeignKey(Skill, on_delete=models.CASCADE)
    message = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.from_user.username} → {self.to_user.username}"



class MockTest(models.Model):

    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    )

    DIFFICULTY_CHOICES = (
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    )

    tutor = models.ForeignKey(Tutor,on_delete=models.CASCADE,related_name='mock_tests')
    title = models.CharField(max_length=200)
    skill = models.ForeignKey(Skill,on_delete=models.SET_NULL,null=True,blank=True,related_name='mock_tests')
    description = models.TextField(blank=True)
    difficulty = models.CharField(max_length=20,choices=DIFFICULTY_CHOICES,default='medium')
    questions = models.JSONField(default=list)
    total_questions = models.IntegerField(default=10)
    passing_score = models.IntegerField(default=70)
    duration_minutes = models.IntegerField(default=30)
    marks_per_question = models.IntegerField(default=1)
    show_result_immediately = models.BooleanField(default=True)
    status = models.CharField( max_length=20,choices=STATUS_CHOICES,default='draft')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title




class TestAttempt(models.Model):
    student = models.ForeignKey(Profile,on_delete=models.CASCADE,related_name='test_attempts')
    test = models.ForeignKey(MockTest,on_delete=models.CASCADE,related_name='attempts')
    score = models.IntegerField(default=0)
    passed = models.BooleanField(default=False)
    attempted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} - {self.test.title}"
    

class Certificate(models.Model):

    student = models.ForeignKey(Profile,on_delete=models.CASCADE,related_name='certificates')
    test = models.ForeignKey(MockTest,on_delete=models.CASCADE,related_name='certificates')
    score = models.FloatField(default=0)
    tutor = models.ForeignKey(Tutor,on_delete=models.CASCADE,related_name='certificates')
    payment_status = models.CharField(max_length=20,default="pending")
    certificate_name = models.CharField(max_length=200)
    certificate_id = models.CharField(max_length=50,unique=True)
    issued_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} - {self.certificate_name}"
    

class SwapMeeting(models.Model):
    swap_request = models.OneToOneField(SkillSwapRequest,on_delete=models.CASCADE,related_name="meeting")
    meeting_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    meeting_link = models.URLField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Meeting for {self.swap_request}"





class CertificateRequest(models.Model):

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved by Tutor'),
        ('rejected', 'Rejected'),
        ('paid', 'Payment Completed'),
        ('completed', 'Certificate Issued'),
    )

    student = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='certificate_requests'
    )

    test = models.ForeignKey(
        MockTest,
        on_delete=models.CASCADE,
        related_name='certificate_requests'
    )

    tutor = models.ForeignKey(
        Tutor,
        on_delete=models.CASCADE,
        related_name='certificate_requests'
    )

    attempt = models.ForeignKey(
        TestAttempt,
        on_delete=models.CASCADE,
        related_name='certificate_request'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    razorpay_order_id = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    razorpay_payment_id = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    payment_amount = models.IntegerField(
        default=199
    )

    requested_at = models.DateTimeField(
        auto_now_add=True
    )

    paid_at = models.DateTimeField(
        blank=True,
        null=True
    )

    def __str__(self):
        return f"{self.student.username} - {self.test.title}"