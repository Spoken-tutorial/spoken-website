import { Injectable } from '@angular/core';
import { Router, NavigationStart } from '@angular/router';
import { Observable, Subject } from 'rxjs';

@Injectable()
export class AlertService {
  private subject = new Subject<any>();
  private keepAfterNavigationChange = false;

  constructor(private router: Router) {
    // clear alert message on route change
    router.events.subscribe(event => {
      if (event instanceof NavigationStart) {
        if (this.keepAfterNavigationChange) {
          // only keep for a single location change
          this.keepAfterNavigationChange = false;
        } else {
          // clear alert
          this.subject.next();
        }
      }
    });
  }

  success(message: string, keepAfterNavigationChange = false) {
    this.keepAfterNavigationChange = keepAfterNavigationChange;
    // this.subject.next({ type: 'success', text: message });
    new Noty({
      type: 'success',
      layout: 'topRight',
      theme: 'metroui',
      closeWith: ['click'],
      text: message,
      animation: {
        open: 'animated fadeInRight',
        close: 'animated fadeOutRight'
      },
      timeout: 4000,
      killer: true
    }).show();
  }

  errorWithMessage(message: string, keepAfterNavigationChange = false) {
    this.keepAfterNavigationChange = keepAfterNavigationChange;
    // this.subject.next({ type: 'error', text: message });
    new Noty({
      type: 'success',
      layout: 'topRight',
      theme: 'metroui',
      closeWith: ['click'],
      text: message,
      animation: {
        open: 'animated fadeInRight',
        close: 'animated fadeOutRight'
      },
      timeout: 4000,
      killer: true
    }).show();
  }

  error(err: any, keepAfterNavigationChange = false) {
    const message = err.error.message || err.statusText;

    this.keepAfterNavigationChange = keepAfterNavigationChange;
    // this.subject.next({ type: 'error', text: message });

    new Noty({
      type: 'error',
      layout: 'topRight',
      theme: 'metroui',
      closeWith: ['click'],
      text: message,
      animation: {
        open: 'animated fadeInRight',
        close: 'animated fadeOutRight'
      },
      timeout: 4000,
      killer: true
    }).show();
  }

  getMessage(): Observable<any> {
    return this.subject.asObservable();
  }
}