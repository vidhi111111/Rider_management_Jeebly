
import { Injectable } from '@angular/core';
import {
  HttpEvent,
  HttpHandler,
  HttpInterceptor,
  HttpRequest,
  HttpErrorResponse
} from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { Router } from '@angular/router';

@Injectable()
export class AuthInterceptor implements HttpInterceptor {
  private isRedirecting = false;

  constructor(private readonly router: Router) {}

  intercept(
    request: HttpRequest<any>,
    next: HttpHandler
  ): Observable<HttpEvent<any>> {
    const token = localStorage.getItem('access_token');

    const authRequest = token
      ? request.clone({
          setHeaders: {
            Authorization: `Bearer ${token}`
          }
        })
      : request;

    return next.handle(authRequest).pipe(
      catchError((error: HttpErrorResponse) => {
        const url = request.url.toLowerCase();

        const isAuthEndpoint =
          url.includes('/login') ||
          url.includes('/register');

        if (
          error.status === 401 &&
          !isAuthEndpoint &&
          !this.isRedirecting
        ) {
          this.isRedirecting = true;

          localStorage.removeItem('access_token');
          localStorage.removeItem('current_user');

          this.router.navigateByUrl('/login').finally(() => {
            this.isRedirecting = false;
          });
        }

        return throwError(() => error);
      })
    );
  }
}
