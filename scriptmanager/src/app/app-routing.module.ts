import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { HomeComponent } from './home/home.component';
import { CreateScriptComponent } from './create-script/create-script.component';
import { EditScriptComponent } from './edit-script/edit-script.component';

const routes: Routes = [
  {
    path: '',
    component: HomeComponent,
    data: {
      title: 'List of Tutorials',
      animation: 'HomePage'
    }
  },
  {
    path: 'createScripts/:id',
    component: CreateScriptComponent,
    data: {
      title: 'Create Script',
      animation: 'HomePage'
    }
  },

  {
    path: 'editScripts',
    component: EditScriptComponent,
    data: {
      title: 'Edit Script',
      animation: 'HomePage'
    }
  }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
