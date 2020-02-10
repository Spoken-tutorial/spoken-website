import { HttpClientModule, HTTP_INTERCEPTORS } from '@angular/common/http';
import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { HomeComponent } from './home/home.component';
import { TutorialsComponent } from './home/tutorials/tutorials.component';
import { JwtModule } from '@auth0/angular-jwt';
import { NgHttpLoaderModule } from 'ng-http-loader';
import { ScriptComponent } from './script/script.component';
import { ScriptSlideComponent } from './script/script-slide/script-slide.component';
import { ScriptCreateComponent } from './script/script-create/script-create.component';
import { ScriptEditComponent } from './script/script-edit/script-edit.component';
import { SweetAlert2Module } from '@sweetalert2/ngx-sweetalert2';
import { ScriptViewComponent } from './script/script-view/script-view.component';
import { ScriptCommentComponent } from './script/script-comment/script-comment.component';
import { CKEditorModule } from '@ckeditor/ckeditor5-angular';
import { ScriptRevisionComponent } from './script/script-revision/script-revision.component';
import { ScriptUploadComponent } from './script/script-upload/script-upload.component';
import { NgxDiffModule } from 'ngx-diff';
import { NgxTextDiffModule } from 'ngx-text-diff';
import { DiffMatchPatchModule } from 'ng-diff-match-patch';
import { CookieModule } from 'ngx-cookie';
import { QuillModule } from 'ngx-quill';
import { BadgeButtonComponent } from './badge-button/badge-button.component'
import { AuthGuard } from './_guards/auth.guard';
import { ErrorInterceptor } from './_interceptors/error.interceptor';
import { PublishedScriptsComponent } from './home/published-scripts/published-scripts.component';
import { ReviewScriptsComponent } from './home/review-scripts/review-scripts.component';
import { ScriptCommentBoxComponent } from './script/script-comment/script-comment-box/script-comment-box.component';
import { AlertService } from './services/alert.service';

// since we are saving the JWT token for authentication in the local storage 
// , here we get that token to send it with each api call to authenticate with the server
export function tokenGetter() {
  const token = localStorage.getItem('token');
  return token;
}

@NgModule({
  declarations: [
    AppComponent,
    HomeComponent,
    TutorialsComponent,
    ScriptComponent,
    ScriptSlideComponent,
    ScriptCreateComponent,
    ScriptEditComponent,
    ScriptViewComponent,
    ScriptCommentComponent,
    ScriptRevisionComponent,
    ScriptUploadComponent,
    BadgeButtonComponent,
    PublishedScriptsComponent,
    ReviewScriptsComponent,
    ScriptCommentBoxComponent,
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    HttpClientModule,
    JwtModule.forRoot({
      config: {
        tokenGetter: tokenGetter,
        whitelistedDomains: ['localhost:8000'],
        blacklistedRoutes: ['']
      }
    }),
    RouterModule,
    FormsModule,
    ReactiveFormsModule,
    NgHttpLoaderModule.forRoot(),
    SweetAlert2Module.forRoot(),
    CKEditorModule,
    NgxDiffModule,
    NgxTextDiffModule,
    DiffMatchPatchModule,
    CookieModule.forRoot(),
    QuillModule.forRoot()
  ],
  providers: [
    AuthGuard,
    { provide: HTTP_INTERCEPTORS, useClass: ErrorInterceptor, multi: true },
    AlertService
  ],
  bootstrap: [AppComponent]
})

export class AppModule {

}
