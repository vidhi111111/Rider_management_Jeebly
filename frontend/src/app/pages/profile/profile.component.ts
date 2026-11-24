import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import {
  FormBuilder,
  FormGroup,
  Validators,
  ReactiveFormsModule
} from '@angular/forms';
import { ProfileService } from '../../core/services/profile.service';
import { LanguageService } from '../../core/services/language.service';

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './profile.component.html',
  styleUrls: ['./profile.component.css']
})
export class ProfileComponent implements OnInit {
  profileForm!: FormGroup;

  loadingProfile = false;
  updatingProfile = false;

  successMessage = '';
  errorMessage = '';

  userEmail = '';
  userName = '';

  avatarPreview: string | null = null;
  isFieldsUpdated = false;

  constructor(
    private fb: FormBuilder,
    private profileService: ProfileService,
    public langService: LanguageService
  ) {}

  ngOnInit(): void {
    this.avatarPreview = localStorage.getItem('profile_avatar') || null;

    this.profileForm = this.fb.group({
      name: ['', [
        Validators.required,
        Validators.maxLength(100)
      ]],
      mobile: ['', [
        Validators.required,
        Validators.pattern(/^[0-9]{10}$/)
      ]]
    });

    this.loadProfile();
  }

  loadProfile(): void {
    this.loadingProfile = true;
    this.clearMessages();

    this.profileService.getProfile().subscribe({
      next: (response: any) => {
        const user = response?.user ?? response?.data ?? response;

        this.profileForm.patchValue({
          name: user?.name || '',
          mobile: user?.mobile || ''
        });

        this.userName = user?.name || '';
        this.userEmail = user?.email || '';

        const dbAvatar = user?.profile_image || user?.avatar || null;
        if (dbAvatar) {
          this.avatarPreview = dbAvatar;
          localStorage.setItem('profile_avatar', dbAvatar);
        } else {
          this.avatarPreview = localStorage.getItem('profile_avatar') || null;
        }

        this.updateStoredUser({
          name: this.userName,
          email: this.userEmail,
          mobile: user?.mobile || '',
          profile_image: this.avatarPreview,
          avatar: this.avatarPreview
        });

        this.loadingProfile = false;
      },
      error: (error) => {
        this.errorMessage =
          error?.error?.message || 'Unable to load profile.';
        this.loadingProfile = false;
      }
    });
  }

  onAvatarSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files[0]) {
      const file = input.files[0];

      if (!file.type.startsWith('image/')) {
        this.errorMessage = 'Please select a valid image file.';
        return;
      }

      if (file.size > 5 * 1024 * 1024) {
        this.errorMessage = 'Image size should be less than 5MB.';
        return;
      }

      // Show immediate local preview
      const reader = new FileReader();
      reader.onload = () => {
        this.avatarPreview = reader.result as string;
      };
      reader.readAsDataURL(file);

      // Persist to backend server / database
      this.profileService.uploadAvatar(file).subscribe({
        next: (res: any) => {
          const user = res?.data || res?.user || res;
          const photoUrl = user?.profile_image || user?.avatar || this.avatarPreview;
          if (photoUrl) {
            this.avatarPreview = photoUrl;
            localStorage.setItem('profile_avatar', photoUrl);
            this.updateStoredUser({ profile_image: photoUrl, avatar: photoUrl });
          }
          this.clearMessages();
          this.successMessage = 'Profile photo uploaded and saved successfully.';
          this.triggerFieldHighlight();
        },
        error: (err) => {
          this.errorMessage = err?.error?.message || 'Unable to upload profile photo.';
        }
      });
    }
  }

  removeAvatar(): void {
    this.profileService.removeAvatar().subscribe({
      next: () => {
        this.avatarPreview = null;
        localStorage.removeItem('profile_avatar');
        this.updateStoredUser({ profile_image: null, avatar: null });
        this.clearMessages();
        this.successMessage = 'Profile photo removed successfully.';
      },
      error: (err) => {
        this.errorMessage = err?.error?.message || 'Unable to remove profile photo.';
      }
    });
  }

  triggerFieldHighlight(): void {
    this.isFieldsUpdated = true;
    setTimeout(() => {
      this.isFieldsUpdated = false;
    }, 3000);
  }

  updateProfile(): void {
    this.clearMessages();

    if (this.profileForm.invalid) {
      this.profileForm.markAllAsTouched();
      return;
    }

    this.updatingProfile = true;

    const payload = {
      name: String(this.profileForm.value.name || '').trim(),
      mobile: String(this.profileForm.value.mobile || '').trim()
    };

    this.profileService.updateProfile(payload).subscribe({
      next: (response: any) => {
        const responseUser =
          response?.user ?? response?.data ?? response;

        const updatedName = responseUser?.name || payload.name;
        const updatedMobile =
          responseUser?.mobile || payload.mobile;

        this.userName = updatedName;
        this.userEmail = responseUser?.email || this.userEmail;

        this.profileForm.patchValue({
          name: updatedName,
          mobile: updatedMobile
        });

        if (responseUser?.profile_image) {
          this.avatarPreview = responseUser.profile_image;
          localStorage.setItem('profile_avatar', responseUser.profile_image);
        }

        this.updateStoredUser({
          ...responseUser,
          name: updatedName,
          email: this.userEmail,
          mobile: updatedMobile,
          profile_image: this.avatarPreview,
          avatar: this.avatarPreview
        });

        this.triggerFieldHighlight();
        this.successMessage =
          response?.message || 'Profile updated successfully.';

        this.updatingProfile = false;
      },
      error: (error) => {
        this.errorMessage =
          error?.error?.message || 'Unable to update profile.';
        this.updatingProfile = false;
      }
    });
  }

  private updateStoredUser(updatedFields: any): void {
    try {
      const storageKeys = ['current_user', 'user'];

      for (const key of storageKeys) {
        const storedValue = localStorage.getItem(key);

        if (!storedValue) {
          continue;
        }

        const storedUser = JSON.parse(storedValue);

        if (
          storedUser &&
          typeof storedUser === 'object' &&
          !Array.isArray(storedUser)
        ) {
          localStorage.setItem(
            key,
            JSON.stringify({
              ...storedUser,
              ...updatedFields
            })
          );
        }
      }
    } catch (error) {
      console.error('Unable to update stored user information.', error);
    }
  }

  getInitial(): string {
    return (this.userName || 'U').charAt(0).toUpperCase();
  }

  clearMessages(): void {
    this.successMessage = '';
    this.errorMessage = '';
  }
}
