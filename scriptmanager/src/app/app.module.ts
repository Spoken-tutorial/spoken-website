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
import { EditScriptComponent } from './edit-script/edit-script.component';
import { NgHttpLoaderModule } from 'ng-http-loader';

export function tokenGetter() {
  const token = localStorage.getItem('token');
  return token;
}

@NgModule({
  declarations: [
    AppComponent,
    HomeComponent,
    TutorialsComponent,
    CreateScriptComponent,
    EditScriptComponent
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
    NgHttpLoaderModule.forRoot()
   
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }

