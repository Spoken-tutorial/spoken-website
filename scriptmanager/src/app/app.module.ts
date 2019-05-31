import { HttpClientModule } from '@angular/common/http';
import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { TutorialsComponent } from './tutorials/tutorials.component';
import { FormsModule } from '@angular/forms';
import { JwtModule } from '@auth0/angular-jwt';

const appRoutes: Routes = [
  {
    path: '',
    component: TutorialsComponent,
    data: {
      title: 'List of Tutorials',
      animation: 'HomePage'
    }
  }
]

export function tokenGetter() {
  return localStorage.getItem('token');
}

@NgModule({
  declarations: [
    AppComponent,
    TutorialsComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    HttpClientModule,
    JwtModule.forRoot({
      config: {
        tokenGetter: tokenGetter,
        whitelistedDomains: [''],
        blacklistedRoutes: ['']
      }
    }),
    RouterModule.forRoot(appRoutes),
    FormsModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }

