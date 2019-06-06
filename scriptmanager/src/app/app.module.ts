import { HttpClientModule } from '@angular/common/http';
import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { FormsModule ,ReactiveFormsModule} from '@angular/forms';
import { HomeComponent } from './home/home.component';
import { TutorialsComponent } from './home/tutorials/tutorials.component';
import { JwtModule } from '@auth0/angular-jwt';
import { CreateScriptComponent } from './create-script/create-script.component';

const appRoutes: Routes = [
  {
    path: '',
    component: HomeComponent,
    data: {
      title: 'List of Tutorials',
      animation: 'HomePage'
    }
  },
  {
    path: 'createScripts',
    component: CreateScriptComponent,
    data: {
      title: 'Create Script',
      animation: 'HomePage'
    }
  }
]

export function tokenGetter() {
  const token = localStorage.getItem('token');
  console.log(token);
  return token;
}

@NgModule({
  declarations: [
    AppComponent,
    HomeComponent,
    TutorialsComponent,
    CreateScriptComponent
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
    RouterModule.forRoot(appRoutes),
    FormsModule,
    ReactiveFormsModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }

