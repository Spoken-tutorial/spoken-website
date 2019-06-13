import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { CreateScriptService } from 'src/app/_service/create-script.service';

// import {NgNoty, NotyOptions} from "ng-noty";

@Component({
  selector: 'app-script-create',
  templateUrl: './script-create.component.html',
  styleUrls: ['./script-create.component.sass']
})
export class ScriptCreateComponent implements OnInit {
  public slides: any = [];
  private id: number;

  constructor(
    private route: ActivatedRoute,
    public createscriptService: CreateScriptService,
    public router:Router
  ) {   }

  public onSaveScript(script: any) {
    for (var i = 0; i < script.length; i++) {
      script[i]['order'] = i+1;
    }

    this.createscriptService.postScript(
      this.id,
      {
        "data": script
      }
    ).subscribe(
      (res)=>{
        this.router.navigateByUrl("/");
      }
    );

  }

  ngOnInit() {
    this.route.params.subscribe(params => {
      this.id = +params['id'];
    });
  }

}
