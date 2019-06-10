import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { HomeComponent } from './home/home.component';
import { CreateScriptComponent } from './create-script/create-script.component';
import { EditScriptComponent } from './edit-script/edit-script.component';
import { ScriptComponent } from './script/script.component';
import { ScriptCreateComponent } from './script/script-create/script-create.component';
import { ScriptEditComponent } from './script/script-edit/script-edit.component';

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
    path: 'create/:id',
    component: ScriptCreateComponent,
    data: {
      title: 'Create Script',
      animation: 'HomePage'
    }
  },

  {
    path: 'edit/:id',
    component: ScriptEditComponent,
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
